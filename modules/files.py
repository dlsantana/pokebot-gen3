import json
import os
from pathlib import Path

from modules.context import context
from modules.pokemon import Pokemon


def read_file(file: Path) -> str | None:
    """
    Simple function to read data from a file, return False if file doesn't exist
    :param file: File to read
    :return: File's contents (str) or None if any kind of error occurred
    """
    try:
        if os.path.exists(file):
            with open(file, mode="r", encoding="utf-8") as open_file:
                return open_file.read()
        else:
            return None
    except:
        return None


def write_file(file: Path, value: str, mode: str = "w") -> bool:
    """
    Simple function to write data to a file, will create the file if doesn't exist.
    Writes to a temp file, then performs os.replace to prevent corruption of files (atomic operations).

    :param file: File to write to
    :param value: Value to write to file
    :param mode: Write mode
    :return: True if file was written to successfully, otherwise False (bool)
    """

    tmp_file = str(f"{file}.tmp")
    try:
        directory = os.path.dirname(tmp_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(tmp_file, mode=mode, encoding="utf-8") as save_file:
            save_file.write(value)
            save_file.flush()
            os.fsync(save_file.fileno())

        os.replace(tmp_file, file)

    except:
        return False

    finally:
        if os.path.exists(tmp_file):
            try:
                os.unlink(tmp_file)
            except:
                pass
        return True


def save_pk3(pokemon: Pokemon) -> None:
    """
    Takes the byte data of [obj]Pokémon.data and outputs it in a pkX format in the /profiles/[PROFILE]/pokemon dir.
    """
    pokemon_dir_path = context.profile.path / "pokemon"
    if not pokemon_dir_path.exists():
        pokemon_dir_path.mkdir()

    pk3_file = f"{pokemon.species.national_dex_number}"
    if pokemon.is_shiny:
        pk3_file = f"{pk3_file} ★"

    pk3_file = pokemon_dir_path / (
        f"{pk3_file} - {pokemon.name} - {pokemon.nature} "
        f"[{pokemon.ivs.sum()}] - {hex(pokemon.personality_value)[2:].upper()}.pk3"
    )

    if os.path.exists(pk3_file):
        os.remove(pk3_file)

    # Open the file and write the data
    with open(pk3_file, "wb") as binary_file:
        binary_file.write(pokemon.data)


def get_rng_state_history() -> list:
    default = []
    try:
        file = read_file(context.profile.path / "soft_reset_frames.json")
        data = json.loads(file) if file else default
        return data
    except SystemExit:
        raise
    except:
        return default


def save_rng_state_history(data: list) -> bool:
    if write_file(context.profile.path / "soft_reset_frames.json", json.dumps(data)):
        return True
    else:
        return False
