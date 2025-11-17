from typing import TypedDict, List, Dict

class ChangeDataType(TypedDict):
    filepath: str
    timestamp: str
    diff: List

class ChangeNotesType(TypedDict):
    normal: ChangeDataType
    important: ChangeDataType