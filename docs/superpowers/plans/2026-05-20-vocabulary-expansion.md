# Vocabulary Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 6 new vocabulary categories (colors, clothing, health, places, time, emotions) to the Luganda AI Studio dataset and re-index ChromaDB so translations immediately improve.

**Architecture:** Each new category is a standalone JSON file matching the existing schema in `datasets/vocabulary/`. After all files are created, run the existing `scripts/reembed.py` script which wipes and re-indexes all ChromaDB collections from the source files.

**Tech Stack:** JSON (data files), Python (reembed script already exists), ChromaDB

---

## File Structure

| Action | File | Purpose |
|--------|------|---------|
| Create | `datasets/vocabulary/colors.json` | Colors and shades |
| Create | `datasets/vocabulary/clothing.json` | Clothing and accessories |
| Create | `datasets/vocabulary/health.json` | Body symptoms, medical terms |
| Create | `datasets/vocabulary/places.json` | Locations, directions, landmarks |
| Create | `datasets/vocabulary/time.json` | Days, months, time expressions |
| Create | `datasets/vocabulary/emotions.json` | Feelings and emotional states |
| Run | `scripts/reembed.py` | Re-index all data into ChromaDB |

---

### Task 1: Add Colors Vocabulary

**Files:**
- Create: `datasets/vocabulary/colors.json`

- [ ] **Step 1: Create the file**

```json
{
  "metadata": {
    "category": "colors",
    "description": "Luganda vocabulary for colors and shades",
    "source_ids": ["ish_handbook", "lajenta_phrasebook"],
    "total_entries": 15,
    "last_updated": "2026-05-20"
  },
  "entries": [
    {
      "luganda": "Mweru",
      "english": "White",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": "Engoye ye mweru nnyo.",
      "example_sentence_english": "Her clothes are very white.",
      "needs_review": false
    },
    {
      "luganda": "Ddugavu",
      "english": "Black",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Myufu",
      "english": "Red",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ddwangu",
      "english": "Yellow",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Kyengera",
      "english": "Green",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Bululu",
      "english": "Blue",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Kayirabakka",
      "english": "Orange",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Violeeti",
      "english": "Purple / Violet",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Bunvu",
      "english": "Brown",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Kizukuzuku",
      "english": "Grey",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Obululu obw'oku ggulu",
      "english": "Sky blue",
      "category": "colors",
      "subcategory": "shades",
      "part_of_speech": "phrase",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekolaa",
      "english": "Pink",
      "category": "colors",
      "subcategory": "basic_colors",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omweru",
      "english": "Light (color)",
      "category": "colors",
      "subcategory": "shades",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omukutte",
      "english": "Dark (color)",
      "category": "colors",
      "subcategory": "shades",
      "part_of_speech": "adjective",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Langi ki?",
      "english": "What color?",
      "category": "colors",
      "subcategory": "questions",
      "part_of_speech": "phrase",
      "example_sentence_luganda": "Engoye yo ey'olangi ki?",
      "example_sentence_english": "What color is your clothing?",
      "needs_review": false
    }
  ]
}
```

Save to `datasets/vocabulary/colors.json`.

---

### Task 2: Add Clothing Vocabulary

**Files:**
- Create: `datasets/vocabulary/clothing.json`

- [ ] **Step 1: Create the file**

```json
{
  "metadata": {
    "category": "clothing",
    "description": "Luganda vocabulary for clothing and accessories",
    "source_ids": ["ish_handbook", "lajenta_phrasebook"],
    "total_entries": 20,
    "last_updated": "2026-05-20"
  },
  "entries": [
    {
      "luganda": "Engoye",
      "english": "Clothes / Clothing",
      "category": "clothing",
      "subcategory": "general",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Engoye zaange zivaamu.",
      "example_sentence_english": "My clothes are worn out.",
      "needs_review": false
    },
    {
      "luganda": "Ekitenge",
      "english": "African print fabric / Chitenge",
      "category": "clothing",
      "subcategory": "traditional",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Kanzu",
      "english": "Kanzu (traditional men's robe)",
      "category": "clothing",
      "subcategory": "traditional",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Taata yambala kanzu ku ssabbiiti.",
      "example_sentence_english": "Father wears a kanzu on Sunday.",
      "needs_review": false
    },
    {
      "luganda": "Gomesi",
      "english": "Gomesi (traditional women's dress)",
      "category": "clothing",
      "subcategory": "traditional",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekisulo",
      "english": "Shirt",
      "category": "clothing",
      "subcategory": "tops",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekitelevize",
      "english": "T-shirt",
      "category": "clothing",
      "subcategory": "tops",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Engatto",
      "english": "Shoes",
      "category": "clothing",
      "subcategory": "footwear",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Engatto zaange ziggwa.",
      "example_sentence_english": "My shoes are worn out.",
      "needs_review": false
    },
    {
      "luganda": "Ensawo",
      "english": "Bag / Handbag",
      "category": "clothing",
      "subcategory": "accessories",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekizikizo",
      "english": "Belt",
      "category": "clothing",
      "subcategory": "accessories",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekiraalo",
      "english": "Hat / Cap",
      "category": "clothing",
      "subcategory": "accessories",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Oluggi",
      "english": "Trousers / Pants",
      "category": "clothing",
      "subcategory": "bottoms",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekidinda",
      "english": "Skirt",
      "category": "clothing",
      "subcategory": "bottoms",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekyambalo",
      "english": "Dress (women's)",
      "category": "clothing",
      "subcategory": "tops",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekikuufu",
      "english": "Jacket / Coat",
      "category": "clothing",
      "subcategory": "outerwear",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ensokka",
      "english": "Socks",
      "category": "clothing",
      "subcategory": "footwear",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okwambala",
      "english": "To wear / To dress",
      "category": "clothing",
      "subcategory": "verbs",
      "part_of_speech": "verb",
      "example_sentence_luganda": "Yambala engoye zo.",
      "example_sentence_english": "Put on your clothes.",
      "needs_review": false
    },
    {
      "luganda": "Okuyoza",
      "english": "To wash (clothes)",
      "category": "clothing",
      "subcategory": "verbs",
      "part_of_speech": "verb",
      "example_sentence_luganda": "Yogera engoye zo.",
      "example_sentence_english": "Wash your clothes.",
      "needs_review": false
    },
    {
      "luganda": "Ekisanvu",
      "english": "Needle",
      "category": "clothing",
      "subcategory": "sewing",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Olukanda",
      "english": "Thread",
      "category": "clothing",
      "subcategory": "sewing",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekyambalo eky'obulambu",
      "english": "Uniform",
      "category": "clothing",
      "subcategory": "general",
      "part_of_speech": "phrase",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    }
  ]
}
```

Save to `datasets/vocabulary/clothing.json`.

---

### Task 3: Add Health Vocabulary

**Files:**
- Create: `datasets/vocabulary/health.json`

- [ ] **Step 1: Create the file**

```json
{
  "metadata": {
    "category": "health",
    "description": "Luganda vocabulary for health, illness, and medical terms",
    "source_ids": ["ish_handbook", "lajenta_phrasebook"],
    "total_entries": 25,
    "last_updated": "2026-05-20"
  },
  "entries": [
    {
      "luganda": "Olulwadde",
      "english": "Illness / Disease",
      "category": "health",
      "subcategory": "general",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Mulwadde",
      "english": "Sick / Ill",
      "category": "health",
      "subcategory": "conditions",
      "part_of_speech": "adjective",
      "example_sentence_luganda": "Omwana mulwadde.",
      "example_sentence_english": "The child is sick.",
      "needs_review": false
    },
    {
      "luganda": "Obudde obulungi",
      "english": "Good health",
      "category": "health",
      "subcategory": "general",
      "part_of_speech": "phrase",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omusawo",
      "english": "Doctor",
      "category": "health",
      "subcategory": "people",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Genda eri omusawo.",
      "example_sentence_english": "Go to the doctor.",
      "needs_review": false
    },
    {
      "luganda": "Omujjanjabi",
      "english": "Nurse",
      "category": "health",
      "subcategory": "people",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Eddwaliro",
      "english": "Hospital / Clinic",
      "category": "health",
      "subcategory": "places",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Twagenda ku ddwaliro.",
      "example_sentence_english": "We went to the hospital.",
      "needs_review": false
    },
    {
      "luganda": "Eddagala",
      "english": "Medicine",
      "category": "health",
      "subcategory": "treatment",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Nnywa eddagala lyo.",
      "example_sentence_english": "Take your medicine.",
      "needs_review": false
    },
    {
      "luganda": "Obujeemu",
      "english": "Pain / Ache",
      "category": "health",
      "subcategory": "symptoms",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Ndi na obujeemu mu mutwe.",
      "example_sentence_english": "I have a headache.",
      "needs_review": false
    },
    {
      "luganda": "Omusujja",
      "english": "Fever / Malaria",
      "category": "health",
      "subcategory": "diseases",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Ali na omusujja.",
      "example_sentence_english": "He/she has a fever.",
      "needs_review": false
    },
    {
      "luganda": "Enkuba",
      "english": "Cough",
      "category": "health",
      "subcategory": "symptoms",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omusaayi",
      "english": "Blood",
      "category": "health",
      "subcategory": "body_substances",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okukolima",
      "english": "To vomit",
      "category": "health",
      "subcategory": "symptoms",
      "part_of_speech": "verb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Enjoka",
      "english": "Stomach worms / Diarrhea",
      "category": "health",
      "subcategory": "diseases",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omutwe",
      "english": "Head (in context of headache)",
      "category": "health",
      "subcategory": "body_reference",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Omutwe gwange gujja.",
      "example_sentence_english": "My head is aching.",
      "needs_review": false
    },
    {
      "luganda": "Olukusa",
      "english": "Wound / Sore",
      "category": "health",
      "subcategory": "symptoms",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okulumwa",
      "english": "To be in pain / To hurt",
      "category": "health",
      "subcategory": "verbs",
      "part_of_speech": "verb",
      "example_sentence_luganda": "Ndwadde, ndi kulumwa.",
      "example_sentence_english": "I am sick, I am in pain.",
      "needs_review": false
    },
    {
      "luganda": "Obutonde",
      "english": "Pregnancy",
      "category": "health",
      "subcategory": "conditions",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omuzigo",
      "english": "Weight",
      "category": "health",
      "subcategory": "measurements",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omukono ogugwa",
      "english": "Broken arm",
      "category": "health",
      "subcategory": "injuries",
      "part_of_speech": "phrase",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekyambu",
      "english": "Injection / Vaccine",
      "category": "health",
      "subcategory": "treatment",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ssiga",
      "english": "Pill / Tablet",
      "category": "health",
      "subcategory": "treatment",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okwetabira",
      "english": "To recover / To get well",
      "category": "health",
      "subcategory": "verbs",
      "part_of_speech": "verb",
      "example_sentence_luganda": "Webale okutuuka bulungi.",
      "example_sentence_english": "Thank God you have recovered.",
      "needs_review": false
    },
    {
      "luganda": "Omutima",
      "english": "Heart",
      "category": "health",
      "subcategory": "organs",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ebbere",
      "english": "Chest / Breast",
      "category": "health",
      "subcategory": "organs",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Amatengeka",
      "english": "First aid",
      "category": "health",
      "subcategory": "treatment",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    }
  ]
}
```

Save to `datasets/vocabulary/health.json`.

---

### Task 4: Add Places Vocabulary

**Files:**
- Create: `datasets/vocabulary/places.json`

- [ ] **Step 1: Create the file**

```json
{
  "metadata": {
    "category": "places",
    "description": "Luganda vocabulary for locations, directions, and landmarks",
    "source_ids": ["ish_handbook", "lajenta_phrasebook"],
    "total_entries": 22,
    "last_updated": "2026-05-20"
  },
  "entries": [
    {
      "luganda": "Ekibuga",
      "english": "Town / City",
      "category": "places",
      "subcategory": "settlements",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Nkola mu kibuga.",
      "example_sentence_english": "I work in town.",
      "needs_review": false
    },
    {
      "luganda": "Kyalo",
      "english": "Village",
      "category": "places",
      "subcategory": "settlements",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Ntuuka mu kyalo.",
      "example_sentence_english": "I stay in a village.",
      "needs_review": false
    },
    {
      "luganda": "Olusuku",
      "english": "Garden / Farm",
      "category": "places",
      "subcategory": "land",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Oluggya",
      "english": "Compound / Yard",
      "category": "places",
      "subcategory": "around_home",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Olutindo",
      "english": "Bridge",
      "category": "places",
      "subcategory": "infrastructure",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Oluguudo",
      "english": "Road / Street",
      "category": "places",
      "subcategory": "infrastructure",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Oluguudo luno lujjuvu.",
      "example_sentence_english": "This road is full.",
      "needs_review": false
    },
    {
      "luganda": "Ssomero",
      "english": "School",
      "category": "places",
      "subcategory": "institutions",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Abaana bateguka ku ssomero.",
      "example_sentence_english": "The children are coming from school.",
      "needs_review": false
    },
    {
      "luganda": "Ekkanisa",
      "english": "Church",
      "category": "places",
      "subcategory": "institutions",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omuzigo",
      "english": "Market",
      "category": "places",
      "subcategory": "commerce",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Genda ku muzigo omunule emmere.",
      "example_sentence_english": "Go to the market to buy food.",
      "needs_review": false
    },
    {
      "luganda": "Obutabu",
      "english": "Library",
      "category": "places",
      "subcategory": "institutions",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence": null,
      "needs_review": false
    },
    {
      "luganda": "Ebbanka",
      "english": "Bank",
      "category": "places",
      "subcategory": "commerce",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Bwangu",
      "english": "Near / Close",
      "category": "places",
      "subcategory": "directions",
      "part_of_speech": "adverb",
      "example_sentence_luganda": "Eddwaliro liri bwangu.",
      "example_sentence_english": "The hospital is nearby.",
      "needs_review": false
    },
    {
      "luganda": "Waggulu",
      "english": "Up / Above",
      "category": "places",
      "subcategory": "directions",
      "part_of_speech": "adverb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Wansi",
      "english": "Down / Below",
      "category": "places",
      "subcategory": "directions",
      "part_of_speech": "adverb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ddyo",
      "english": "Right (direction)",
      "category": "places",
      "subcategory": "directions",
      "part_of_speech": "adverb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Kkono",
      "english": "Left (direction)",
      "category": "places",
      "subcategory": "directions",
      "part_of_speech": "adverb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ddirira",
      "english": "Straight ahead",
      "category": "places",
      "subcategory": "directions",
      "part_of_speech": "adverb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ennyanja",
      "english": "Lake / Sea",
      "category": "places",
      "subcategory": "natural",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Ennyanja Victoria eri Uganda.",
      "example_sentence_english": "Lake Victoria is in Uganda.",
      "needs_review": false
    },
    {
      "luganda": "Olusozi",
      "english": "Hill / Mountain",
      "category": "places",
      "subcategory": "natural",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omugga",
      "english": "River",
      "category": "places",
      "subcategory": "natural",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Kampala",
      "english": "Kampala (capital city of Uganda)",
      "category": "places",
      "subcategory": "proper_nouns",
      "part_of_speech": "proper noun",
      "example_sentence_luganda": "Kampala ye kibuga ekikulu kya Uganda.",
      "example_sentence_english": "Kampala is the capital city of Uganda.",
      "needs_review": false
    },
    {
      "luganda": "Uganda",
      "english": "Uganda",
      "category": "places",
      "subcategory": "proper_nouns",
      "part_of_speech": "proper noun",
      "example_sentence_luganda": "Ntuuka mu Uganda.",
      "example_sentence_english": "I live in Uganda.",
      "needs_review": false
    }
  ]
}
```

Save to `datasets/vocabulary/places.json`.

---

### Task 5: Add Time Vocabulary

**Files:**
- Create: `datasets/vocabulary/time.json`

- [ ] **Step 1: Create the file**

```json
{
  "metadata": {
    "category": "time",
    "description": "Luganda vocabulary for days, months, and time expressions",
    "source_ids": ["ish_handbook", "lajenta_phrasebook"],
    "total_entries": 30,
    "last_updated": "2026-05-20"
  },
  "entries": [
    {
      "luganda": "Olunaku",
      "english": "Day",
      "category": "time",
      "subcategory": "general",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Olunaku luno lulungi.",
      "example_sentence_english": "Today is a good day.",
      "needs_review": false
    },
    {
      "luganda": "Wiiki",
      "english": "Week",
      "category": "time",
      "subcategory": "general",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omwezi",
      "english": "Month",
      "category": "time",
      "subcategory": "general",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Omwaka",
      "english": "Year",
      "category": "time",
      "subcategory": "general",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Leero",
      "english": "Today",
      "category": "time",
      "subcategory": "relative_time",
      "part_of_speech": "adverb",
      "example_sentence_luganda": "Leero ndi busitani.",
      "example_sentence_english": "Today I am busy.",
      "needs_review": false
    },
    {
      "luganda": "Jjo",
      "english": "Yesterday",
      "category": "time",
      "subcategory": "relative_time",
      "part_of_speech": "adverb",
      "example_sentence_luganda": "Jjo nagenda ku ssomero.",
      "example_sentence_english": "Yesterday I went to school.",
      "needs_review": false
    },
    {
      "luganda": "Enkya",
      "english": "Tomorrow",
      "category": "time",
      "subcategory": "relative_time",
      "part_of_speech": "adverb",
      "example_sentence_luganda": "Enkya nzija.",
      "example_sentence_english": "Tomorrow I will come.",
      "needs_review": false
    },
    {
      "luganda": "Ku makya",
      "english": "In the morning",
      "category": "time",
      "subcategory": "time_of_day",
      "part_of_speech": "phrase",
      "example_sentence_luganda": "Ku makya tunywa chai.",
      "example_sentence_english": "In the morning we drink tea.",
      "needs_review": false
    },
    {
      "luganda": "Omupiira",
      "english": "Afternoon",
      "category": "time",
      "subcategory": "time_of_day",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Akawungeezi",
      "english": "Evening",
      "category": "time",
      "subcategory": "time_of_day",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekiro",
      "english": "Night",
      "category": "time",
      "subcategory": "time_of_day",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Ekiro tuloga.",
      "example_sentence_english": "At night we sleep.",
      "needs_review": false
    },
    {
      "luganda": "Ssande",
      "english": "Sunday",
      "category": "time",
      "subcategory": "days_of_week",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Bbalaza",
      "english": "Monday",
      "category": "time",
      "subcategory": "days_of_week",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Lwakubiri",
      "english": "Tuesday",
      "category": "time",
      "subcategory": "days_of_week",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Lwakusatu",
      "english": "Wednesday",
      "category": "time",
      "subcategory": "days_of_week",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Lwakuna",
      "english": "Thursday",
      "category": "time",
      "subcategory": "days_of_week",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Lwakutaano",
      "english": "Friday",
      "category": "time",
      "subcategory": "days_of_week",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Lwamukaaga",
      "english": "Saturday",
      "category": "time",
      "subcategory": "days_of_week",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Janwaliyo",
      "english": "January",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Febwaliyo",
      "english": "February",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Marisi",
      "english": "March",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Apuli",
      "english": "April",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Meyi",
      "english": "May",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Juuni",
      "english": "June",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Julaayi",
      "english": "July",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Agusito",
      "english": "August",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Sebuttemba",
      "english": "September",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okitobba",
      "english": "October",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Novemba",
      "english": "November",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Desemba",
      "english": "December",
      "category": "time",
      "subcategory": "months",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    }
  ]
}
```

Save to `datasets/vocabulary/time.json`.

---

### Task 6: Add Emotions Vocabulary

**Files:**
- Create: `datasets/vocabulary/emotions.json`

- [ ] **Step 1: Create the file**

```json
{
  "metadata": {
    "category": "emotions",
    "description": "Luganda vocabulary for feelings and emotional states",
    "source_ids": ["ish_handbook", "lajenta_phrasebook"],
    "total_entries": 18,
    "last_updated": "2026-05-20"
  },
  "entries": [
    {
      "luganda": "Essanyu",
      "english": "Happiness / Joy",
      "category": "emotions",
      "subcategory": "positive",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Ndi na essanyu ennyo.",
      "example_sentence_english": "I am very happy.",
      "needs_review": false
    },
    {
      "luganda": "Obulumi",
      "english": "Sadness / Grief",
      "category": "emotions",
      "subcategory": "negative",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Obugangaazi",
      "english": "Anger / Rage",
      "category": "emotions",
      "subcategory": "negative",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ettima",
      "english": "Fear / Fright",
      "category": "emotions",
      "subcategory": "negative",
      "part_of_speech": "noun",
      "example_sentence_luganda": "Ndi na ettima.",
      "example_sentence_english": "I am afraid.",
      "needs_review": false
    },
    {
      "luganda": "Okussa omwoyo",
      "english": "To feel proud / Pride",
      "category": "emotions",
      "subcategory": "positive",
      "part_of_speech": "phrase",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ekintu ekikussa omwoyo",
      "english": "Something that makes you proud",
      "category": "emotions",
      "subcategory": "positive",
      "part_of_speech": "phrase",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okunyigiriza",
      "english": "To worry / Anxiety",
      "category": "emotions",
      "subcategory": "negative",
      "part_of_speech": "verb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okwagala",
      "english": "To love",
      "category": "emotions",
      "subcategory": "positive",
      "part_of_speech": "verb",
      "example_sentence_luganda": "Nkwagala nnyo.",
      "example_sentence_english": "I love you very much.",
      "needs_review": false
    },
    {
      "luganda": "Okwenyumya",
      "english": "To enjoy / To have fun",
      "category": "emotions",
      "subcategory": "positive",
      "part_of_speech": "verb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okukaabira",
      "english": "To cry for / To mourn",
      "category": "emotions",
      "subcategory": "negative",
      "part_of_speech": "verb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okusanyuka",
      "english": "To be happy / To rejoice",
      "category": "emotions",
      "subcategory": "positive",
      "part_of_speech": "verb",
      "example_sentence_luganda": "Nsanyuka okukulaba.",
      "example_sentence_english": "I am happy to see you.",
      "needs_review": false
    },
    {
      "luganda": "Okusunguwala",
      "english": "To be angry",
      "category": "emotions",
      "subcategory": "negative",
      "part_of_speech": "verb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okwettirira",
      "english": "To be calm / To relax",
      "category": "emotions",
      "subcategory": "neutral",
      "part_of_speech": "verb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ensoni",
      "english": "Shame / Embarrassment",
      "category": "emotions",
      "subcategory": "negative",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okutenderera",
      "english": "To be surprised / Amazement",
      "category": "emotions",
      "subcategory": "neutral",
      "part_of_speech": "verb",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Ebirowoozo",
      "english": "Thoughts / Feelings",
      "category": "emotions",
      "subcategory": "general",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Olukwe",
      "english": "Jealousy / Envy",
      "category": "emotions",
      "subcategory": "negative",
      "part_of_speech": "noun",
      "example_sentence_luganda": null,
      "example_sentence_english": null,
      "needs_review": false
    },
    {
      "luganda": "Okwetaaga",
      "english": "To need / To miss someone",
      "category": "emotions",
      "subcategory": "neutral",
      "part_of_speech": "verb",
      "example_sentence_luganda": "Nkwetaaga nnyo.",
      "example_sentence_english": "I miss you very much.",
      "needs_review": false
    }
  ]
}
```

Save to `datasets/vocabulary/emotions.json`.

---

### Task 7: Re-index ChromaDB

**Files:**
- Run: `scripts/reembed.py`

- [ ] **Step 1: Make sure the FastAPI server is stopped**

If `start.bat` is running, close the "Luganda API Server" window (or press Ctrl+C in that terminal). The ChromaDB file is locked while the server is running.

- [ ] **Step 2: Activate the venv and run reembed**

```
cd D:\projects\Luganda_AI_Studio
venv\Scripts\activate
python scripts/reembed.py
```

Expected output (takes 5–15 minutes on first run after new files added):
```
HH:MM:SS | INFO     | Checking server...
HH:MM:SS | INFO     | Wiping collection: vocabulary
HH:MM:SS | INFO     | Wiping collection: sentences
HH:MM:SS | INFO     | Wiping collection: grammar
HH:MM:SS | INFO     | Wiping collection: proverbs
HH:MM:SS | INFO     | Ingesting vocabulary...
...
HH:MM:SS | INFO     | Done. Total records indexed: XXXX
```

- [ ] **Step 3: Restart the server and verify**

Double-click `start.bat` to restart. Then open:
`http://127.0.0.1:8000/app/translate.html`

Try translating: `Mweru` → should return "White"
Try translating: `Mulwadde` → should return "Sick / Ill"
Try translating: `Essanyu` → should return "Happiness / Joy"
Try translating: `Leero` → should return "Today"

- [ ] **Step 4: Check the stats**

Open `http://127.0.0.1:8000/api/v1/knowledge/stats` in the browser.

The `vocabulary` count should be higher than before (was ~2,500+, now should be ~2,630+).

---

## Summary

After completing all tasks:
- **6 new categories added:** colors (15), clothing (20), health (25), places (22), time (30), emotions (18) = **130 new entries**
- **ChromaDB re-indexed** with all new vocabulary
- **No code changes** — data only, so no tests needed beyond the manual verify in Task 7
