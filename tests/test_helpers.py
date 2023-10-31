import os

import pytest
from dotenv import find_dotenv, load_dotenv

import lib.helpers

load_dotenv(find_dotenv())


def test_get_valid_date__formats():
    # '%m/%d/%y'
    given_date = "1/13/23"
    assert lib.helpers.get_valid_date(given_date), "Format: 1/13/23 should be valid"

    given_date = "01/13/23"
    assert lib.helpers.get_valid_date(given_date), "Format: 01/13/23 should be valid"

    # '%m/%d/%Y'
    given_date = "01/13/2023"
    assert lib.helpers.get_valid_date(given_date), "Format: 01/13/2023 should be valid"

    given_date = "1/13/2023"
    assert lib.helpers.get_valid_date(given_date), "Format: 1/13/2023 should be valid"

    # '%Y-%m-%d'
    given_date = "2023-01-13"
    assert lib.helpers.get_valid_date(given_date), "Format: 2023-01-13 should be valid"

    given_date = "23-01-13"  # Invalid date
    assert (
        lib.helpers.get_valid_date(given_date) is None
    ), "Format 23-01-13 should be invalid"


def test_trim_and_split_string():
    test_string = (
        "word1,word2   , word3 word4"  # Badly formatted but should be correctly split
    )
    assert lib.helpers.trim_and_split_string(test_string) == [
        "word1",
        "word2",
        "word3",
        "word4",
    ]


def test_build_url():
    # build_url(type: str, id: str, action: str = None)
    id = "NotRandomGoogleDocID"
    # Spreadsheet, no action
    type = "spreadsheets"
    assert (
        lib.helpers.build_url(type, id)
        == "https://docs.google.com/spreadsheets/d/NotRandomGoogleDocID"
    )
    # With action edit
    action = "edit"
    assert (
        lib.helpers.build_url(type, id, action)
        == "https://docs.google.com/spreadsheets/d/NotRandomGoogleDocID/edit"
    )

    # Document, no action
    type = "document"
    assert (
        lib.helpers.build_url(type, id)
        == "https://docs.google.com/document/d/NotRandomGoogleDocID"
    )
    # With action edit
    action = "edit"
    assert (
        lib.helpers.build_url(type, id, action)
        == "https://docs.google.com/document/d/NotRandomGoogleDocID/edit"
    )

    # Slide, no action
    type = "slide"
    assert (
        lib.helpers.build_url(type, id)
        == "https://docs.google.com/slide/d/NotRandomGoogleDocID"
    )
    # With action edit
    action = "edit"
    assert (
        lib.helpers.build_url(type, id, action)
        == "https://docs.google.com/slide/d/NotRandomGoogleDocID/edit"
    )

    # Unknown type
    type = "Unknown"
    assert (
        lib.helpers.build_url(type, id, action)
        == "https://drive.google.com/open?id=NotRandomGoogleDocID"
    )


def test_get_google_type_from_mimetype():
    #'application/vnd.google-apps.document': 'document',
    assert (
        lib.helpers.get_google_type_from_mimetype(
            "application/vnd.google-apps.document"
        )
        == "document"
    )
    #'application/vnd.google-apps.file': 'file',
    assert (
        lib.helpers.get_google_type_from_mimetype("application/vnd.google-apps.file")
        == "file"
    )
    #'application/vnd.google-apps.folder': '',
    assert (
        lib.helpers.get_google_type_from_mimetype("application/vnd.google-apps.folder")
        == ""
    )
    #'application/vnd.google-apps.presentation': 'slide',
    assert (
        lib.helpers.get_google_type_from_mimetype(
            "application/vnd.google-apps.presentation"
        )
        == "slide"
    )
    #'application/vnd.google-apps.spreadsheet': 'spreadsheets',
    assert (
        lib.helpers.get_google_type_from_mimetype(
            "application/vnd.google-apps.spreadsheet"
        )
        == "spreadsheets"
    )
    assert lib.helpers.get_google_type_from_mimetype("Not/Applicable") == ""


def test_character_name_from_document():
    mock_document = {"title": "Name / Splat"}

    # Document with a properly formatted title
    assert lib.helpers.character_name_from_document(mock_document) == "Name"

    mock_document = {"title": "Invalid Name, Splat"}

    # Document with a badly formatted title
    assert (
        lib.helpers.character_name_from_document(mock_document) == "Invalid Name, Splat"
    )

    # Document without a title
    assert lib.helpers.character_name_from_document({}) == ""


def test_get_id_from_drive_url():
    # https://drive.google.com/open?id=FakeGoogleDocID
    assert (
        lib.helpers.get_id_from_drive_url(
            "https://drive.google.com/open?id=FakeGoogleDocID"
        )
        == "FakeGoogleDocID"
    )
    # https://drive.google.com/drive/folders/FakeGoogleDocID?usp=drive_link
    assert (
        lib.helpers.get_id_from_drive_url(
            "https://drive.google.com/drive/folders/FakeGoogleDocID?usp=drive_link"
        )
        == "FakeGoogleDocID"
    )


def test_get_wiki_url():
    game = "scion"
    character_name = "Some Fake Scion"

    # Existing game
    assert (
        lib.helpers.get_wiki_url(game, character_name)
        == "https://wiki.mythic-saga.com/view/ScD:Some%20Fake%20Scion"
    )

    # Non-existing game
    game = "foo"
    with pytest.raises(ValueError):
        lib.helpers.get_wiki_url(game, character_name)


def test_get_character_row():
    # (game: str, st_sheet_id: str)
    st_sheet_id = "FakeGoogleSheetID"
    # Game does not exist
    game = "foo"
    with pytest.raises(ValueError):
        lib.helpers.get_character_row(game, st_sheet_id)

    game = "scion"
    actual_list_range, actual_value_range_body = lib.helpers.get_character_row(
        game, st_sheet_id
    )
    assert actual_list_range == "Character list!A2:M"
    cols = actual_value_range_body.get("values")[0]
    assert len(cols) == 12
    for i, col in enumerate(cols):
        if i != 5:  # index 5 is url
            assert col[:-4] == '=IMPORTRANGE(INDIRECT(CONCAT("F", ROW())), "Overview!'
        else:
            assert col == "https://docs.google.com/spreadsheets/d/FakeGoogleSheetID"

    game = "exalted"
    actual_list_range, actual_value_range_body = lib.helpers.get_character_row(
        game, st_sheet_id
    )
    assert actual_list_range == "Character list!A2:I"
    cols = actual_value_range_body.get("values")[0]
    assert len(cols) == 9

    for i, col in enumerate(cols):
        if i != 5:  # index 5 is url
            assert col[:-4] == '=IMPORTRANGE(INDIRECT(CONCAT("F", ROW())), "Overview!'
        else:
            assert col == "https://docs.google.com/spreadsheets/d/FakeGoogleSheetID"
