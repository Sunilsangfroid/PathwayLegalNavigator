import logging
import os
import pathway as pw
from dotenv import load_dotenv
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.xpacks.llm.servers import DocumentStoreServer
from pydantic import BaseModel, ConfigDict, InstanceOf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

load_dotenv()
pw.set_license_key(os.environ.get("PW_KEY"))

class App(BaseModel):
    document_store: InstanceOf[DocumentStore]
    host: str = "0.0.0.0"
    port: int = 8000

    with_cache: bool = True
    terminate_on_error: bool = False

    def run(self) -> None:
        server = DocumentStoreServer(self.host, self.port, self.document_store)
        server.run(
            with_cache=self.with_cache,
            terminate_on_error=self.terminate_on_error,
        )
    
    model_config = ConfigDict(extra="forbid")

if __name__ == "__main__":
    with open("app.yaml") as f:
        config = pw.load_yaml(f)
    app = App(**config)
    app.run()
