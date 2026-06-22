from dataclasses import dataclass, field
from datetime import datetime, UTC
import os
from pathlib import Path
import time
#
import docker
from docker.errors import NotFound
import httpx
#
from db_builder import context_hash


DB_DIR = Path("/db")
MAPPING_DIR = Path("/app/config")
BLANKS_DIR = Path("/blanks")
ONTOP_IMAGE = os.getenv("ONTOP_IMAGE", "semantic-data-cloud-ontop")
ONTOP_NETWORK = os.getenv("ONTOP_NETWORK", "dwc-net")
ONTOP_STARTUP_TIMEOUT = float(os.getenv("ONTOP_STARTUP_TIMEOUT", 60))


# NOTE: Simple class to be expanded on, for now just essential info
#
@dataclass
class ContainerInfo:
    container_id: str
    container_name: str
    ontop_url: str
    last_used: datetime = field(default_factory=lambda: datetime.now(UTC))


# NOTE: Main class to contain information about containers
#
class ContainerRegistry:

    def __init__(self):
        self._docker = docker.from_env()
        self._registry: dict[str, ContainerInfo] = {}
        self._host_mounts: dict[str, str] = self._discover_host_mounts()

    # NOTE: The Docker daemon needs host-side paths when mounting volumes into sibling containers
    # Inspect the fastaproxy container for information about these host-side paths 
    #
    def _discover_host_mounts(self) -> dict[str, str]:
        hostname = os.getenv("HOSTNAME")

        self_info = self._docker.containers.get(hostname)
        mounts = {
            m["Destination"]: m["Source"]
            for m in self_info.attrs.get("Mounts", [])
        }
        return mounts

    def get_or_create(
        self,
        dataset_ids: list[str],
    ) -> ContainerInfo:

        ctx_hash = context_hash(dataset_ids)

        # NOTE: Check the in-memory registry first
        #
        info = self._registry.get(ctx_hash)

        if info:
            if self._is_healthy(info.ontop_url):
                info.last_used = datetime.now(UTC)
                return info

        info = self._start(ctx_hash)

        self._registry[ctx_hash] = info
        return info

    def _is_healthy(self, ontop_url: str) -> bool:
        try:
            res = httpx.get(f"{ontop_url}/actuator/health", timeout=3)
            return res.status_code == 200
        except httpx.RequestError:
            return False

    def _wait_for_health(self, ontop_url: str) -> None:
        deadline = time.monotonic() + ONTOP_STARTUP_TIMEOUT
        while time.monotonic() < deadline:
            try:
                res = httpx.get(f"{ontop_url}/actuator/health", timeout=3)
                if res.status_code == 200:
                    return
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(2)
        raise TimeoutError(f"Ontop container at {ontop_url} did not become healthy within {ONTOP_STARTUP_TIMEOUT}s!")

    def _write_properties(self, ctx_hash: str) -> Path:
        template_path = MAPPING_DIR / "dwcowl.properties"

        template = template_path.read_text()

        props = template.replace("dwcowl", ctx_hash)

        props_path = DB_DIR / f"{ctx_hash}.properties"
        props_path.write_text(props)
        return props_path

    def _write_obda(self, ctx_hash: str) -> Path:
        template_path = MAPPING_DIR / "dwcowl.obda"

        template = template_path.read_text()
        obda = template.replace("dwcowl", f'"{ctx_hash}"')

        obda_path = DB_DIR / f"{ctx_hash}.obda"
        obda_path.write_text(obda)
        return obda_path

    def _write_metadata(self, ctx_hash: str) -> Path:

        template = (MAPPING_DIR / "dwcowl.json").read_text()

        metadata = template.replace('\\"dwcowl\\"', f'\\"{ctx_hash}\\"')

        path = DB_DIR / f"{ctx_hash}.metadata.json"
        path.write_text(metadata)

        return path

    def _start(self, ctx_hash: str) -> ContainerInfo:
        props_path = self._write_properties(ctx_hash)
        obda_path = self._write_obda(ctx_hash)
        metadata_path = self._write_metadata(ctx_hash)

        container_name = f"ontop-{ctx_hash}"

        # NOTE: For now force remove any pre-existing container.
        #
        try:
            container = self._docker.containers.get(container_name)
            container.remove(force=True)
        except NotFound:
            pass

        volumes = {
            self._host_mounts.get(str(DB_DIR)): {
                "bind": str(DB_DIR),
                "mode": "rw"
            },
            self._host_mounts.get(str(MAPPING_DIR)): {
                "bind": "/opt/ontop/input/mappings",
                "mode": "ro"
            },
            self._host_mounts.get(str(BLANKS_DIR)): {
                "bind": str(BLANKS_DIR),
                "mode": "ro"
            },
        }

        command = [
            "ontop", "endpoint",
            "-m", f"{str(DB_DIR)}/{obda_path.name}",
            "-t", "/opt/ontop/input/mappings/dwcowl.ttl",
            "-p", f"{str(DB_DIR)}/{props_path.name}",
            "-d", f"{str(DB_DIR)}/{metadata_path.name}",
        ]

        container = self._docker.containers.run(
            image=ONTOP_IMAGE,
            name=container_name,
            detach=True,
            network=ONTOP_NETWORK,
            volumes=volumes,
            command=command,
        )
        ontop_url = f"http://{container_name}:8080"

        self._wait_for_health(ontop_url)

        return ContainerInfo(
            container_id=container.id,
            container_name=container_name,
            ontop_url=ontop_url,
        )
