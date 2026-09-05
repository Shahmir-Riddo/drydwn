import re
from django.db.models import Q, Case, When, Value, IntegerField
from .models import Fragrance

ACRONYM_MAP = {
    'mfk': 'maison francis kurkdjian',
    'jpg': 'jean paul gaultier',
    'ysl': 'yves saint laurent',
    'pdm': 'parfums de marly',
    'tf': 'tom ford',
    'adp': 'acqua di parma',
    'eldo': 'etat libre d orange',
    'cdg': 'comme des garcons',
    'ath': 'aaron terence hughes',
    'br540': 'baccarat rouge 540',
    'bdc': 'bleu de chanel',
    'dhi': 'dior homme intense',
    'swy': 'stronger with you',
    'git': 'green irish tweed',
    'viw': 'virgin island water',
    'ahsee': 'allure homme sport eau extreme',
    'cdnim': 'club de nuit intense man',
}


def search_fragrances(query):
    """
    Intelligent fragrance search supporting:
    - Multi-word queries across house and fragrance name (e.g. 'Lattafa Asad', 'Dior Sauvage')
    - Hyphenated / slugified brand names (e.g. 'jean-paul-gaultier' matching 'Jean Paul Gaultier')
    - Acronym expansions (e.g. 'JPG Le Male', 'TF Tobacco Vanille', 'BR540')
    - Inverted search order (e.g. 'Asad Lattafa', 'Tobacco Vanille Tom Ford')
    - Smart relevance scoring prioritizing exact & prefix matches
    """
    raw_query = (query or '').strip()
    if not raw_query:
        return Fragrance.objects.none()

    clean_q = raw_query.lower()

    # Expand known fragrance/house acronyms
    for acr, expansion in ACRONYM_MAP.items():
        clean_q = re.sub(r'\b' + re.escape(acr) + r'\b', expansion, clean_q)

    # Normalize separators (convert hyphens, slashes, underscores to spaces)
    normalized = re.sub(r'[\-_/.]+', ' ', clean_q)
    tokens = [t.strip() for t in normalized.split() if t.strip()]

    if not tokens:
        return Fragrance.objects.none()

    # Build AND filter: every token must match either the fragrance name or the house name
    q_filter = Q()
    for t in tokens:
        # Match against name or house (both normal and hyphenated)
        t_hyphen = t.replace(' ', '-')
        q_filter &= (
            Q(name__icontains=t) |
            Q(house__name__icontains=t) |
            Q(house__name__icontains=t_hyphen)
        )

    qs = Fragrance.objects.filter(q_filter).select_related('house')

    # Build relevance ranking
    whens = [
        When(name__iexact=raw_query, then=Value(1000)),
        When(name__istartswith=raw_query, then=Value(800)),
        When(name__icontains=raw_query, then=Value(600)),
    ]

    # If multi-token query, rank by matching sub-phrases of fragrance name
    if len(tokens) > 1:
        for i in range(len(tokens)):
            for j in range(len(tokens), i, -1):
                phrase = ' '.join(tokens[i:j])
                if phrase.lower() == raw_query.lower():
                    continue
                phrase_len = j - i
                whens.append(When(name__iexact=phrase, then=Value(500 + phrase_len * 20)))
                whens.append(When(name__istartswith=phrase, then=Value(400 + phrase_len * 20)))
                whens.append(When(name__icontains=phrase, then=Value(300 + phrase_len * 20)))

    whens.extend([
        When(house__name__iexact=raw_query, then=Value(200)),
        When(house__name__istartswith=raw_query, then=Value(150)),
    ])

    return qs.annotate(
        relevance=Case(*whens, default=Value(10), output_field=IntegerField())
    ).order_by('-relevance', 'name')
