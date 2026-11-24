"""Compare spoken words without treating spelling variants or digits as omissions."""
import re,unicodedata
NUMBERS=dict(zip(['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty'],map(str,range(21))))|{'thirty':'30','forty':'40','fifty':'50','sixty':'60','seventy':'70','eighty':'80','ninety':'90','hundred':'100'}
def normalize(text):
 text=unicodedata.normalize('NFKD',text.replace('–','-').replace('—','-')).encode('ascii','ignore').decode().lower().replace("'",'').replace('%',' percent ')
 text=re.sub(r'\b('+ '|'.join(NUMBERS)+r')\b',lambda m:NUMBERS[m[0]],text);text=re.sub(r'[^a-z0-9 ]',' ',text)
 for a,b in [('behaviour','behavior'),('recognise','recognize'),('practise','practice'),('labelled','labeled'),('modelling','modeling'),('organisation','organization'),('colour','color')]:text=text.replace(a,b)
 text=re.sub(r'\bjoe\b','jo',text);text=re.sub(r'\bjoes\b','jos',text)
 return ' '.join(text.split())
def words(text):return normalize(text).split()
