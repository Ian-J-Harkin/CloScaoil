import re
import json

raw_text = """[l.31]: #

# An Turas go Manannán

Tráṫnóna aoiḃinn i ndeire an Earraiġ timċeall
bliana ina ḋiaiḋ san ḃí Seán Ó Maolċaṫa ag
feiṫeaṁ leis an mbeirt eile ag an aer-ṗort i mBaile
Uí Coileáin. Ḃí ḋuine ḋe ġiollaí an aer-ṗuirt ag
líonaḋ umar an eitealláin ḋe petrol, agus Ḃí Seán féin
ag ċur gaċ aon niḋ i n-órdú agus i n-eagar i gcoṁair an
turais éaċtaiġ a ḃí roimis.
Ḃí tuitim na hoiḋċe ann agus ḃí na réilṫíní geala a
dteasbáint féin san aer ina gceann is ina gceann. Ḃí
corrán gealaiġe croċta ós ċionn na gcrann taoḃ ṫall
ḋe ṗáirc na n-eiteallán.
“Is breáġ an t-eiteallán é seo, a ḋuine uasail,”
arsa an giolla i gceann tamaill.
“Ní foláir nó taoi ag cuiṁneaṁ ar ḋul ar aistear ḟada ann.
An id’ aonar a raġair?”

“Beiḋ beirt eile faram,” arsa Seán.
“Cogar, a ḋuine uasail. An do’n Mol Ṫuaiḋ a raġaiḋ siḃ?”
"""

def dehyphenate(text):
    return re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2\n', text)

def apply_global_replacements(text):
    # Mimic the config
    text = text.replace('ſ', 's')
    # punctuation_spacing
    text = re.sub(r'[ \t]+([?!.,:;])', r'\1', text)
    text = re.sub(r'([?!.,:;])[ \t]+', r'\1 ', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text

print("--- After Dehyphenate ---")
step1 = dehyphenate(raw_text)
print(step1[:500])

print("\n--- After Global Replacements ---")
step2 = apply_global_replacements(step1)
print(step2[:500])

# Check line 11/12 join in step1
print("\nCheck join 11/12 in step1:", "roimis.\nḂí" in step1)
print("Check join 11/12 in step2:", "roimis.\nḂí" in step2)
