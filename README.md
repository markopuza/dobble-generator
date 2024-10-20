## How to use

#### To generate playing cards

1. Populate the `/img` folder with your Dobble png images (with transparent background), prefixed `1_` to `57_`
2. Run `preprocess_img.py`
3. Run `generate_cards.py`. The `/cards` folder will be populated with playing cards.

#### To generate explanation cards
1. Populate `symbols.txt` with desired explanations, prefixed `> 1. ` to `> 57. `
2. Run `generate_explanation_cards.py`, potentially fine-tuning the parameters within the code