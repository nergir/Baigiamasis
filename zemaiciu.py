import enchant
from enchant.checker import SpellChecker

base_dict = "lt_LT"
pwl_path = "zemaiciu.txt"
d = enchant.DictWithPWL(base_dict, pwl_path)

f = open("metai.txt", encoding="utf-8")
text = f.readline()
f.close()

text += " Plints Pabonga Kinis Klecks randomnas"

for word in text.split():
    if d.check(word):
        print(f"'{word}' is recognized.")
    else:
        print(f"'{word}' is not recognized.")

chkr = SpellChecker(d)

# Set the text to check
print(text)
chkr.set_text(text)

# Iterate over errors and print them
for err in chkr:
    print("ERROR:", err.word)
