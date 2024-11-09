import os, json, logging, shutil

from graphrag_sdk.models.gemini import GeminiGenerativeModel
from graphrag_sdk.models.ollama import OllamaGenerativeModel
from graphrag_sdk.models.openai import OpenAiGenerativeModel
from graphrag_sdk.model_config import KnowledgeGraphModelConfig
from graphrag_sdk import KnowledgeGraph
from graphrag_sdk.ontology import Ontology

from src.ingestion.source import CustomSource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_ONT_PATH = "db/ontology.json"
DB_FILES_PATH = "db/files"
OLLAMA_ADDR = "http://localhost:11434"


class Processor:
    def __init__(self, load_mode: bool) -> None:
        self.load_mode = load_mode
        self.boundaries = """
            Extract only the most relevant information.
            Avoid creating entities for details that can be expressed as attributes.
        """

        if len(os.getenv("OPENAI_API_KEY", "")) != 0:
            self.model = OpenAiGenerativeModel(model_name="gpt-4o-mini")
        elif len(os.getenv("GOOGLE_API_KEY", None)) != 0:
            self.model = GeminiGenerativeModel(model_name="gemini-1.5-flash-001")
        else:
            self.model = OllamaGenerativeModel(model_name="llama3.2", host=OLLAMA_ADDR)

        self.ontology: Ontology | None = self._load_ontology_from_json_file(DB_ONT_PATH)

        self.sources = []
        for file in os.listdir(DB_FILES_PATH):
            self.sources.append(CustomSource(os.path.join(DB_FILES_PATH, file)))

        self._update_kg()

    def add_files(self, folderpath: str) -> None:
        os.makedirs(DB_FILES_PATH, exist_ok=True)

        new_sources = []

        for filename in os.listdir(folderpath):
            src_path = os.path.join(folderpath, filename)
            if os.path.isdir(src_path):
                continue
            base, ext = os.path.splitext(filename)
            dest_filename = filename
            counter = 1
            while os.path.exists(os.path.join(DB_FILES_PATH, dest_filename)):
                dest_filename = f"{base}_{counter}{ext}"
                counter += 1
            dest_path = os.path.join(DB_FILES_PATH, dest_filename)
            try:
                shutil.copy2(src_path, dest_path)
                new_sources.append(CustomSource(dest_path))
            except Exception as e:
                print(f"Error copying file {filename}: {str(e)}")
                continue
        if new_sources:
            self.sources = new_sources
            self._update_ontology(new_sources)

    def delete_ontology(self):
        open(DB_ONT_PATH, "w").close()

    def delete_files(self):
        for filename in os.listdir(DB_FILES_PATH):
            file_path = os.path.join(DB_FILES_PATH, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))

    def _update_ontology(self, new_sources):
        print("updating ontology!")
        new_ontology = Ontology.from_sources(
            sources=new_sources, model=self.model, boundaries=self.boundaries
        )
        if self.ontology is not None:
            new_ontology.merge_with(self.ontology)
        self.ontology = new_ontology
        self._save_ontology_to_local()
        self._update_kg()

    def _load_ontology_from_json_file(self, file_path: str) -> Ontology | None:
        try:
            with open(file_path, "r") as file:
                json_data = json.load(file)
                file.close()
            return Ontology.from_json(json_data)
        except:
            if self.load_mode:
                return None
            else:
                raise Exception("local ontology file is empty, first add files")

    def _save_ontology_to_local(self):
        with open(os.path.join("db", "ontology.json"), "w", encoding="utf-8") as file:
            json.dump(self.ontology.to_json(), file, indent=2)

    def _update_kg(self):
        if self.ontology is not None:
            self.kg = KnowledgeGraph(
                name="my_kg",
                model_config=KnowledgeGraphModelConfig.with_model(self.model),
                ontology=self.ontology,
            )
            print("processing sources from knowledge graph!")
            self.kg.process_sources(self.sources)

    def ask_question(self, question: str) -> str:
        chat = self.kg.chat_session()
        response = chat.send_message(question)
        return response
