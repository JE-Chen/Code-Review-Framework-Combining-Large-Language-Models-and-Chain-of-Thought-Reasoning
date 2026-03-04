from pathlib import Path


def build_llm_judge_prompt(root_folder: str):
    root_path = Path(root_folder)
    for folder_path in root_path.rglob("*"):
        if "cot" in folder_path.name:
            if folder_path.is_dir():
                for file_path in folder_path.iterdir():
                    if file_path.name == "our_llm_judge.md":
                        file_path.unlink()


if __name__ == "__main__":
    target_folder = "./cot"
    build_llm_judge_prompt(target_folder)
