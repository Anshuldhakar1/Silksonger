import customtkinter as ctk
from typing import List, Tuple, Dict, Any, Optional

# --- Logic Configuration ---
SCENE_KEYS = {
    "playerData.respawnScene",
    "playerData.mapZone",
    "playerData.currentArea",
    "playerData.respawnType",
    "playerData.hazardRespawnFacing",
    "playerData.respawnMarkerName",
    "playerData.HeroCorpseScene",
}

def get_scene_key(item: dict) -> str:
    return f"{item.get('SceneName', 'Unk')}: {item.get('ID', 'Unk')}"

def get_name_key(item: dict) -> str:
    return item.get("Name", "Unknown")

def diff_keyed_list(path: str, old_list: List[Dict], new_list: List[Dict], key_func, value_key="Value") -> List[Tuple]:
    diffs = []
    old_map = {key_func(x): x for x in old_list}
    new_map = {key_func(x): x for x in new_list}
    
    all_keys = set(old_map.keys()) | set(new_map.keys())
    
    for key in all_keys:
        in_old = key in old_map
        in_new = key in new_map
        
        if not in_old and in_new:
            new_item = new_map[key]
            val = new_item.get(value_key) if value_key in new_item else new_item
            diffs.append(("add", path, [(key, val)]))
            
        elif in_old and not in_new:
            old_item = old_map[key]
            val = old_item.get(value_key) if value_key in old_item else old_item
            diffs.append(("remove", path, [(key, val)]))
            
        elif in_old and in_new:
            old_item = old_map[key]
            new_item = new_map[key]
            val_old = old_item.get(value_key) if value_key else old_item
            val_new = new_item.get(value_key) if value_key else new_item
            
            if val_old != val_new:
                friendly_path = f"{path}[{key}]"
                diffs.append(("change", friendly_path, (val_old, val_new)))
                
    return diffs

def compute_save_diff(old_data: Dict, new_data: Dict) -> List[Tuple]:
    if not old_data or not new_data:
        return []

    changes = []
    old_pd = old_data.get("playerData", {})
    new_pd = new_data.get("playerData", {})
    ignored_pd_keys = {"EnemyJournalKillData", "QuestCompletionData", "ToolEquips", "Collectables"}
    
    for k, v_new in new_pd.items():
        if k in ignored_pd_keys: continue
        v_old = old_pd.get(k)
        if v_old != v_new:
            changes.append(("change", f"playerData.{k}", (v_old, v_new)))

    changes.extend(diff_keyed_list(
        "Journal", 
        old_pd.get("EnemyJournalKillData", {}).get("list", []),
        new_pd.get("EnemyJournalKillData", {}).get("list", []),
        get_name_key, value_key="Record"
    ))

    changes.extend(diff_keyed_list(
        "Quest", 
        old_pd.get("QuestCompletionData", {}).get("savedData", []),
        new_pd.get("QuestCompletionData", {}).get("savedData", []),
        get_name_key, value_key="Data"
    ))

    old_sd = old_data.get("sceneData", {})
    new_sd = new_data.get("sceneData", {})
    
    changes.extend(diff_keyed_list("SceneBool", old_sd.get("persistentBools", {}).get("serializedList", []), new_sd.get("persistentBools", {}).get("serializedList", []), get_scene_key, value_key="Value"))
    changes.extend(diff_keyed_list("SceneInt", old_sd.get("persistentInts", {}).get("serializedList", []), new_sd.get("persistentInts", {}).get("serializedList", []), get_scene_key, value_key="Value"))
    changes.extend(diff_keyed_list("GeoRock", old_sd.get("geoRocks", {}).get("serializedList", []), new_sd.get("geoRocks", {}).get("serializedList", []), get_scene_key, value_key="Value"))

    final_changes = []
    scene_change_entry = None
    
    for op, path, val in changes:
        if path == "playerData.respawnScene":
            scene_change_entry = ("change", "SCENE TRANSITION", val)
            break
            
    if scene_change_entry:
        final_changes.append(scene_change_entry)
        
    for op, path, val in changes:
        if scene_change_entry and path in SCENE_KEYS:
            continue
        final_changes.append((op, path, val))

    return final_changes

# --- GUI / Display Section ---

def expanded_format(data, indent: int = 0) -> str:
    step = "    " 
    current_indent = step * indent
    next_indent = step * (indent + 1)

    if isinstance(data, dict):
        if not data: return "{}" 
        lines = ["{"]
        for key, value in data.items():
            lines.append(f"{next_indent}{repr(key)}: {expanded_format(value, indent + 1)},")
        lines.append(f"{current_indent}}}")
        return "\n".join(lines)

    elif isinstance(data, (list, tuple)):
        is_list = isinstance(data, list)
        if not data: return "[]" if is_list else "()"
        
        open_char = "[" if is_list else "("
        close_char = "]" if is_list else ")"
        
        lines = [open_char]
        for item in data:
            lines.append(f"{next_indent}{expanded_format(item, indent + 1)},")
        lines.append(f"{current_indent}{close_char}")
        return "\n".join(lines)
    else:
        return repr(data)

def render_diff_view(scroll_frame: ctk.CTkScrollableFrame, diff_data: List, asset_manager):
    """
    Centralized logic to render the diff list into a scrollable frame.
    """
    # Fonts & Icons
    diff_font = ctk.CTkFont(family="Roboto Mono", size=13, weight="normal")
    diff_font_bold = ctk.CTkFont(family="Roboto Mono", size=13, weight="bold")
    icon_arrow = asset_manager.get_icon("arrow_right")

    def create_change_row(index, path, del_content, add_content, operation, suffix_title=""):
        bg_color = "#f7f7f7" if index % 2 == 0 else "#fcfcfc"
        
        change_frame = ctk.CTkFrame(scroll_frame, fg_color=bg_color)
        change_frame.pack(padx=15, pady=5, fill="x", expand=True)
        change_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_frame = ctk.CTkFrame(change_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=5, pady=0, sticky="ew")

        arrow_label = ctk.CTkLabel(title_frame, text="", image=icon_arrow)
        arrow_label.grid(row=0, column=0, padx=0, pady=0)

        full_title = f"{path}{suffix_title}"
        title_label = ctk.CTkLabel(
            title_frame, 
            text=full_title, 
            fg_color="transparent", 
            font=diff_font_bold,
            text_color="#616161" if not suffix_title else "#888888"
        )
        title_label.grid(row=0, column=1, padx=(3, 0), sticky="w")

        # Values
        values_frame = ctk.CTkFrame(change_frame, fg_color="transparent")
        values_frame.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

        if del_content is not None:
            values_frame.grid_columnconfigure(0, weight=0)
            del_frame = ctk.CTkFrame(values_frame, fg_color="#fdecec", border_width=2, border_color="#656565")
            del_frame.grid(row=0, column=0, padx=5, pady=0, sticky="w")
            
            lbl = ctk.CTkLabel(del_frame, text=f"{del_content} ", text_color="#b81818", font=diff_font)
            lbl.pack(padx=5, pady=2)

        if add_content is not None:
            col = 1 if del_content is not None else 0
            values_frame.grid_columnconfigure(col, weight=0)
            add_frame = ctk.CTkFrame(values_frame, fg_color="#e8f9ef", border_width=2, border_color="#656565")
            add_frame.grid(row=0, column=col, padx=5, pady=0, sticky="w")
            
            fmt_text = expanded_format(add_content)
            lbl = ctk.CTkLabel(add_frame, text=f" {fmt_text}", text_color="#117e3a", font=diff_font, justify="left", anchor="w")
            lbl.pack(padx=(5,8), pady=2)

    # Clear existing content
    for widget in scroll_frame.winfo_children():
        widget.destroy()

    # Populate
    for i, item in enumerate(diff_data):
        operation, path, values = item
        
        if operation == "add":
            total = len(values)
            for idx, sub in enumerate(values):
                batch = f"  [{idx+1}/{total}]" if total > 1 else ""
                create_change_row(i, path, None, sub, operation, batch)
        
        elif operation == "remove":
            total = len(values)
            for idx, sub in enumerate(values):
                batch = f"  [{idx+1}/{total}]" if total > 1 else ""
                create_change_row(i, path, sub, None, operation, batch)
                
        elif operation == "change":
            old, new = values
            create_change_row(i, path, old, new, operation)