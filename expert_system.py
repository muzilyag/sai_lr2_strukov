import json

import questionary

from working_memory import WorkingMemory


class ExpertSystem:
    def __init__(self, kb: str = "./kb.json") -> None:
        self._kb_file: str = kb
        self._kb: list[dict] = []
        self._working_mem: WorkingMemory = WorkingMemory()
        self._load_kb()

    def _load_kb(self) -> None:
        with open(self._kb_file, "r", encoding="utf-8") as f:
            self._kb = json.load(f)
    
    def _save_kb(self) -> None:
        with open(self._kb_file, "w", encoding="utf-8") as f:
            json.dump(self._kb, f, ensure_ascii=False, indent=4)

    def show_kb(self) -> None:
        if not self._kb:
            print("База знаний пуста! Добавьте правила")
            return
        for i in range(len(self._kb)):
            self.show_rule(i + 1)   

    def show_rule(self, id_if: int) -> None:
        if not (0 < id_if <= len(self._kb)):   
            print(f"Неверный номер = {id_if}: ничего не найдено")
            return
        knowledge: dict = self._kb[id_if - 1]
        print(f"Правило #{id_if}:")
        print("\tЕСЛИ:")
        for obj, val in knowledge["if"].items():
            print(f"\t-> {obj}: {val}")
        print("\tТО:")
        print(f"\t-> {knowledge['then']['object']}: {knowledge['then']['value']}\n")

    def add_rule(self, if_dict: dict[str, str], then_obj: str, then_val: str) -> bool:
        new_knowledge: dict = {
            "if": if_dict,
            "then": {
                "object": then_obj,
                "value": then_val
            }
        }
        self._kb.append(new_knowledge)
        self._save_kb()
        print("Правило успешно добавлено")
        return True
    
    def edit_rule(self, id_if: int, new_if: dict[str, str], new_then_obj: str, new_then_val: str) -> bool:
        if not (0 < id_if <= len(self._kb)):   
            print(f"Неверный номер = {id_if}: ничего не найдено")
            return False
        self._kb[id_if - 1] = {
            "if": new_if,
            "then": {
                "object": new_then_obj, 
                "value": new_then_val
            }
        }
        self._save_kb()
        print("Правило успешно изменено")
        return True
        
    def delete_rule(self, id_if: int) -> bool:
        if not (0 < id_if <= len(self._kb)):   
            print(f"Неверный номер = {id_if}: ничего не найдено")
            return False
        self._kb.pop(id_if - 1)
        self._save_kb()
        print("Правило успешно удалено")
        return True

    def show_working_mem(self) -> None:
        print(f"[РАБОЧАЯ ПАМЯТЬ]: {self._working_mem}")

    def init_start_situation(self) -> None:
        self._working_mem.clear()
        self._working_mem.add_fact("показы", "много")
        self._working_mem.add_fact("клики", "мало")

    def run(self) -> None:
        pass