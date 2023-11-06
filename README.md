# Sanctioning character in Mythic Saga (Scion, Exalted or Gunstar-Exalted)

This is a document describing how to use either the more-or-less automatic jupyter notebook, or sanctioning manually. In either way you need to have access to the files, which is granted to all STs in Mythic Saga.

To be able to run the jupyter notebook correctly, you also need to have the `credentials.json` file. Since that one includes secrets pertaining the app, it is not included in the repo, but can be either downloaded via `https://console.cloud.google.com` => Credentials => Mythic Saga App, or (if you don't have access to the app) I can send it to you.

The second important part is `token.json`. If you don't have that file (or are getting errors in Step 1 about invalid_grant), it's because you haven't authorised your google user (or the authorisation has expired). If it's the error version, start by removing the `token.json` file, but **don't touch the credentials**.

## Generating a token.json-file

You need to start by running the cells associated with Imports and Functions, then fill in the necessary variables in Step 1: Editable variables, after which you can run all the cells in Step 1 (one at the time). In the final cell of Step 1 you will get redirected to authorise the app with your google user. This is because the script will have full access to your drive. It does not remove any files, but it does create and change them.

## Running the script

Only two of the steps/cells affect files, namely Step 2 and Step 3, with the other cells either setting up things for later ones, or printing out things you need for manual steps.

The only cell you should need to change is Step 1: Editable variables, with the rest of the things hopefully working as it should.

## Examples
* Dry run with input file: `python sanction.py -dr -v file input/char_list.csv -st Marie`
* Dry run with cli scion character: `python sanction.py -v -dr cli scion -sh 1PwInljF0L67lxWz3VLLSfB7TEmYchsEvnfV0azAeh4o  -st Marie -e marie.hogebrandt@gmail.com -c Creator Monster Sage`
* Get list of files (from Charles' PDF folder): `python drive-ls.py https://drive.google.com/drive/folders/1omckCZDwnXx3ivYiSx55hIU6EoBPpX3s -b view -m -f output/template-links.txt`
* Run the pre-commit scripts in case the pre-commit hook breaks: `pre-commit run --all-files`

## File format
- A text file (or csv) with semicolon-separated rows
- GAME (lowercase);GOOGLE_SHEET_ID; PLAYER_EMAIL; SANCTION_DATE (can be blank); SANCTION_ST (can be blank); CALLINGS (blank if not Scion)
- If SANCTION_DATE is blank and -d is a valid date, it uses that. If -d is not set it uses current date
- If -st is set and SANCTION_ST is set, it chooses the file over the flag
