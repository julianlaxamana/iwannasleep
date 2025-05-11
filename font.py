from PySide6.QtGui import QFontDatabase, QFont

# Load the font file
font_id = QFontDatabase.addApplicationFont("fonts/MyFont.ttf")

# Get the font family name
if font_id != -1:
    family = QFontDatabase.applicationFontFamilies(font_id)[0]
    custom_font = QFont(family, 10)
    app.setFont(custom_font)
    print(f"Loaded custom font: {family}")
else:
    print("Failed to load custom font.")
