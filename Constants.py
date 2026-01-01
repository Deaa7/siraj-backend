CITIES = [
    ('حمص', 'العادية حمص'),
    ("إدلب", "إدلب"),
    ('دمشق', 'دمشق'),
    ('حلب', 'حلب'),
    ('دير الزور', 'دير الزور'),
    ('ريف دمشق', 'ريف دمشق'),
    ("درعا", "درعا"),
    ('طرطوس', 'طرطوس'),
    ("اللاذقية", "اللاذقية"),
    ("الحسكة", "الحسكة"),
    ("قنيطرة", "قنيطرة"),
    # ("السويداء", "السويداء"),
    ("حماة", "حماة"),
    ("الرقة", "الرقة"),
    
]

CITIES_ARRAY = [
    "حمص", "إدلب", "دمشق", "حلب", "دير الزور", "ريف دمشق", "درعا", "طرطوس", "اللاذقية", "الحسكة", "قنيطرة", "حماة", "الرقة"
]

GENDERS = [
    ('M', 'ذكر'),
    ('F', 'أنثى'),
]


GENDERS_ARRAY = [
    "M", "F"
]

LEVELS = [
 ("سهل" , "سهل") ,
 ("متوسط" , "متوسط") ,
 ("صعب" , "صعب") ,
 ]

LEVELS_ARRAY = [
    "سهل", "متوسط", "صعب"
]

CLASSES = [
    ("6", "السادس") ,
    ("7", "السابع") ,
    ("8", "الثامن") ,
    ("9", "التاسع") ,
    ("10", "العاشر") ,
    ("11", "الحادي عشر") ,
    ("12", "بكلوريا") ,
]

CLASSES_ARRAY = [
    "6", "7", "8", "9", "10", "11", "12"
]

CLASSES_DICT = {
    "6": "السادس",
    "7": "السابع",
    "8": "الثامن",
    "9": "التاسع",
    "10": "العاشر",
    "11": "الحادي عشر",
    "12": "بكلوريا",
}

SUBJECT_NAMES = [
    ("math", "الرياضيات") ,
    ("english", "اللغة الإنجليزية") ,
    ("arabic", "اللغة العربية") ,
    ("french", "اللغة الفرنسية") ,
    ("history", "التاريخ") ,
    ("geography", "الجغرافيا") ,
    ("social","اجتماعيات"),
    ("islam" , "الديانة الإسلامية") ,
    ("science", "العلوم") ,
    ("chemistry", " كيمياء") ,
    ("physics", "فيزياء") ,
    ("philosophy" ,"فلسفة") ,
    ("physics_chemistry", "فيزياء و كيمياء") ,
]
 
SUBJECT_NAMES_ARRAY = [
    "math", "english", "arabic", "french", "history", "geography", "social", "islam", "science", "chemistry", "physics", "philosophy", "physics_chemistry"
]
 
 
SUBJECT_NAMES_DICT = {
    "math": "الرياضيات",
    "english": "اللغة الإنجليزية",
    "arabic": "اللغة العربية",
    "french": "اللغة الفرنسية",
    "history": "التاريخ",
    "geography": "الجغرافيا",
    "social": "اجتماعيات",
    "islam": "الديانة الإسلامية",
    "science": "العلوم",
    "chemistry": "كيمياء",
    "physics": "فيزياء",
    "philosophy": "فلسفة",
    "physics_chemistry": "فيزياء و كيمياء",
}



VIDEO_MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB
# Valid video formats
VIDEO_ALLOWED_FORMATS = [
    'video/mp4',
    'video/avi',
    'video/quicktime',  # mov
    'video/x-msvideo',  # avi
    'video/x-ms-wmv',   # wmv
    'video/webm',
    'video/ogg',
    'video/mpeg',
    'video/x-matroska',  # mkv
]

# Valid file extensions (as backup check)
VIDEO_ALLOWED_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv', '.webm', '.ogv', '.mpeg', '.mpg', '.mkv']

IMAGE_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

IMAGE_ALLOWED_FORMATS = [
    'image/jpeg',
    'image/png',
    # 'image/gif',
    'image/webp',
    'image/svg+xml',
    'image/tiff',
    'image/jpg',
]

IMAGE_ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.svg', '.tiff', '.jpg']

PAYMENT_WAYS_ARRAY = ["shamcash", "syriatel", "fauad", "haram"]