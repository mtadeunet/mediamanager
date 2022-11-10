from PySide6.QtCore import Qt

def defineRowColor(record, score):
    if record["last_update"] == 9999999999:
        return Qt.red
    if record["last_update"] == 0 or not record["likes"]:
        return Qt.transparent
    if score < 1:
        return Qt.darkBlue
    if score < 2:
        return Qt.darkGreen
    if score < 3:
        return Qt.darkYellow

    return Qt.darkGray

def defineScore(record, userRecord):
    if record["last_update"] == 9999999999 or record["last_update"] == 0:
        return '-'
    if not record["likes"]:
        return '-'
    return record["likes"] / userRecord.likes
