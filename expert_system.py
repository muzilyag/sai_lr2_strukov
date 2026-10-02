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
        self._working_mem.add_fact("позиция показа", "высокая")
        self._working_mem.add_fact("релевантность текста", "низкая")

    def select_goal(self) -> tuple[str, str] | None:
        goals = dict.fromkeys(
            (rule["then"]["object"], rule["then"]["value"]) for rule in self._kb
        )
        choices = [
            questionary.Choice(f"{obj}: {val}", value=(obj, val))
            for obj, val in goals
        ]
        choices.append(questionary.Choice(">>> Отмена", value=None))
        return questionary.select(
            "Выберите целевую ситуацию (гипотезу) для доказательства:",
            choices=choices
        ).ask()

    def _prove_goal(self, goal_obj: str, goal_val: str, visited: set[tuple[str, str]], depth: int = 0) -> bool:        
        current_val = self._working_mem.get_fact(goal_obj)
        if current_val == goal_val:
            return True
        if current_val is not None:
            return False
        if (goal_obj, goal_val) in visited:
            return False    
        visited.add((goal_obj, goal_val))
        matching_rules = [
            (i, rule) for i, rule in enumerate(self._kb)
            if rule["then"]["object"] == goal_obj and rule["then"]["value"] == goal_val
        ]
        if not matching_rules:
            return False   
        pad = "\t" * depth
        if depth == 0:
            print()
        print(f"{pad}Ищется цель '{goal_obj}: {goal_val}' в заключениях правил")
        for i, rule in matching_rules:
            print(f"{pad}[?] Подходит правило #{i + 1}:")
            for cond_obj, cond_val in rule["if"].items():
                fact_val = self._working_mem.get_fact(cond_obj)
                if fact_val == cond_val:
                    continue
                if fact_val is not None:
                    break 
                print(f"{pad}[!] Не все условия выполнены - новая цель: '{cond_obj}: {cond_val}'")
                if not self._prove_goal(cond_obj, cond_val, visited, depth + 1):
                    break
            else:
                print(f"{pad}[+] Все условия выполнены -> в РБД добавляется факт '{goal_obj}: {goal_val}'")
                self._working_mem.add_fact(goal_obj, goal_val)
                return True
        return False

    def run(self) -> None:
        goal = self.select_goal()
        if not goal:
            return  
        goal_obj, goal_val = goal
        print("Исходная ситуация (РБД):")
        self.show_working_mem()
        print(f"\nЦель (гипотеза):\n  '{goal_obj}: {goal_val}'")
        visited: set[tuple[str, str]] = set()
        is_proven = self._prove_goal(goal_obj, goal_val, visited)
        print("\nРБД после логического вывода:")
        self.show_working_mem()
        if is_proven:
            print(f"\n[success] Т.о., факты достоверны, цель '{goal_obj}: {goal_val}' подтвердилась\n")
        else:
            print(f"\n[failure] Т.о., цель '{goal_obj}: {goal_val}' опровергнута (недостижима при данных условиях)\n")