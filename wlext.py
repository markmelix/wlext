import argparse
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

parser = argparse.ArgumentParser("wlext")
parser.add_argument("wordlist")
args = parser.parse_args()

input = args.wordlist
output = f"{input}.csv"
failput = f"{input}.failed.txt"

with open(input) as inlist, open(output, mode="w") as outlist, open(
    failput, mode="w"
) as failedlist:
    inlines = inlist.readlines()
    outlines = []
    failed = []
    done = set()

    print(f"Words to proceed: {len(inlines)}")

    for i, word in enumerate(inlines):
        word = word.rstrip("\n")

        if word in done:
            continue

        url = f"https://wooordhunt.ru/word/{word}"
        resp = requests.get(url, verify=False)

        if resp.status_code != 200:
            failed.append(f"{word}\n")
            print(f"{i + 1} > Failed {word}")
            continue

        soup = BeautifulSoup(resp.text, "lxml")

        transcription = soup.find(attrs={"class": "transcription"})
        translation = soup.find(attrs={"class": "t_inline_en"})

        try:
            final_transcription = transcription.text.strip().strip("|")
            final_translation = translation.text.strip()
            outlines.append(
                f'"{word}"; "{final_transcription}"; "{final_translation}"\n'
            )
            print(f"{i + 1} Done {word} - {final_transcription} - {final_translation}")
        except AttributeError:
            failed.append(f"{word}\n")
            print(f"{i + 1} > Failed {word}")
            continue

        done.add(word)

    outlist.writelines(outlines)
    failedlist.writelines(failed)
