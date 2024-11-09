import argparse, os, logging
from dotenv import load_dotenv

from src.processor import Processor


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main(args):
    try:
        load_mode = True if args.folder else False
        processor = Processor(load_mode)

        if args.delete_files:
            print("delete all internal files")
            processor.delete_files()
            return
        if args.delete_ontology:
            print("delete ontology")
            processor.delete_ontology()
            return

        if args.folder:
            print("adding more files")
            folder_path = args.folder
            processor.add_files(folder_path)

        print("\033[92mWelcome to your local GraphRAG System!\033[0m")  # Green text
        print("Commands:")
        print("  'quit' or 'exit' - End the program")
        print("  'help' - Show this help message")
        print("  'clear' - Clear the console")
        print("-" * 50)

        while True:
            try:
                user_input = input("\033[94m>\033[0m ").strip()
                if user_input.lower() in ["quit", "exit"]:
                    print("\033[92mGoodbye!\033[0m")
                    break
                elif user_input.lower() == "help":
                    print("\n\033[93mCommands:\033[0m")
                    print("  'quit' or 'exit' - End the program")
                    print("  'help' - Show this help message")
                    print("  'clear' - Clear the console")
                    continue
                elif user_input.lower() == "clear":
                    os.system("cls" if os.name == "nt" else "clear")
                    continue
                if not user_input:
                    continue
                try:
                    response = processor.ask_question(user_input)
                    print("\n\033[92mResponse:\033[0m", response)
                except Exception as e:
                    error_msg = f"Error processing input: {str(e)}"
                    logging.error(error_msg)
                    print(f"\033[91m{error_msg}\033[0m")
            except KeyboardInterrupt:
                print("\n\033[92mGoodbye!\033[0m")
                break
            except EOFError:
                print("\n\033[93mInput stream ended.\033[0m")
                break
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logging.error(error_msg)
                print(f"\n\033[91m{error_msg}\033[0m")
                print("Please try again.")

    except ValueError as e:
        print("error while loading ontology")
        print(e)
    except Exception as e:
        print("there was an error")
        print(e)
    finally:
        exit("program terminated. have a nice day")


if __name__ == "__main__":
    load_dotenv()
    setup_logging()
    os.environ["SCARF_NO_ANALYTICS"] = "true"  # ensure privacy from unstructured io
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--folder", help="path to folder with files")
    parser.add_argument(
        "--delete-files",
        help="delete all local files",
        action="store_true",
    )
    parser.add_argument(
        "--delete-ontology",
        help="delete the generated ontology",
        action="store_true",
    )
    parser.add_argument(
        "-q", "--question", help="the question you want to ask your trained model"
    )

    args = parser.parse_args()
    main(args)
