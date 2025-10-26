VANCOUVER_CITIES = {
    "Vancouver",
    "Burnaby",
    "Richmond",
    "Surrey",
    "Coquitlam",
    "Port Coquitlam",
    "Port Moody",
    "New Westminster",
    "North Vancouver",
    "West Vancouver",
    "Delta",
    "White Rock",
    "Langley",
    "Maple Ridge",
    "Pitt Meadows",
    "Tsawwassen",
}

# Order matters for how we display options
CUISINE_TYPES = [
    "Indian",
    "Chinese",
    "Thai",
    "Greek",
    "Korean",
    "Vietnamese",
    "Japanese",
    "American",
    "Italian",
    "French",
    "Canadian",
    "Others",
]

# Keywords to detect each cuisine from the free-text categories field
CUISINE_KEYWORDS = {
    "Indian": ["indian", "punjabi", "pakistani", "bangladeshi"],
    "Chinese": ["chinese", "szechuan", "cantonese", "dim sum"],
    "Thai": ["thai"],
    "Greek": ["greek", "mediterranean"],
    "Korean": ["korean", "bbq korean", "korean bbq"],
    "Vietnamese": ["vietnamese", "pho", "banh mi"],
    "Japanese": ["japanese", "sushi", "ramen", "izakaya"],
    "American": ["american", "burgers", "bbq", "diner"],
    "Italian": ["italian", "pizza", "pasta"],
    "French": ["french", "bistro"],
    "Canadian": ["canadian", "poutine"],
}
