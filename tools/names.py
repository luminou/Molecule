import re
FIX = {
 "2,2'6'triCBPA":"2,2',6-TriCBPA","2,2'diCBPA":"2,2'-DiCBPA","2,4'diCBPA":"2,4'-DiCBPA","2monoCBPA":"2-MonoCBPA",
 "2,4DDD":"2,4'-DDD","2,4DDE":"2,4'-DDE","2,4DDT":"2,4'-DDT","4,4DDD":"4,4'-DDD","4,4DDE":"4,4'-DDE","4,4DDT":"4,4'-DDT",
 "4,4'oxydiphenol":"4,4'-Oxydiphenol","Acetaminophene":"Acetaminophen","Acetylsalicylic acid":"Aspirin",
 "Alachlore":"Alachlor","Benzophenone 1":"Benzophenone-1","Benzophenone 2":"Benzophenone-2","Benzophenone 3":"Benzophenone-3",
 "Chlorosulfuron":"Chlorsulfuron","Chlorpyriphos":"Chlorpyrifos","Cischlordane":"cis-Chlordane","Cisnonachlore":"cis-Nonachlor",
 "Diclofopmethyl":"Diclofop-methyl","Ibuprofene":"Ibuprofen","Indomethacine":"Indomethacin","Lindane ou HCH":"Lindane",
 "Methoxychlore":"Methoxychlor","Metolachlore":"Metolachlor","Myrex":"Mirex","Nonafluorobutane-1-sulfonic acid":"PFBS",
 "PFunDA":"PFUnDA","Penconazol":"Penconazole","Terbutylazine":"Terbuthylazine","Toldofos-methyl":"Tolclofos-methyl",
 "Toxaphen":"Toxaphene","Transchlordane":"trans-Chlordane","Transnonachlor":"trans-Nonachlor","Triflurnizole":"Triflumizole",
 "Tri-o-tolyl phosphate":"ToTP","TmCP":"TmTP","TpCP":"TpTP","TCP":"Tricresyl phosphate","T 0901317":"T0901317",
 "WAY 252623":"WAY-252623","RU 486":"RU486","CP 775146":"CP 775,146","Bis(2-hydroxyphenyl)methane":"2,2'-BPF",
 "Heptachlor endo-epoxide":"Heptachlor endo-epoxide","Fipronil sulfone":"Fipronil sulfone",
}
def clean(n):
    if not isinstance(n, str): return n
    s = re.sub(r"\s*\([^)]*\)\s*$", "", n).strip()
    m = re.match(r"^Australie (\d+)$", s)
    if m: return f"Blind study sample {m.group(1)}"
    return FIX.get(s, s)
