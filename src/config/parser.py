#!/usr/bin/env python3


from secrets import randbits


class MazeConfig:
    """A class to hold the configuration for maze generation."""
    def __init__(
            self, width: int, height: int, entry: tuple[int, int],
            exit_pos: tuple[int, int], output_file: str,
            perfect: bool, seed: int):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
        self.output_file = output_file
        self.perfect = perfect
        self.seed = seed

    @classmethod
    def from_config(cls, file_path: str) -> "MazeConfig":
        """Reads the configuration from a file
        and returns a MazeConfig instance."""
        config: dict[str, str] = {}
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
        if config == {}:
            raise ValueError("Configuration file is empty or "
                             "contains no valid entries.")
        try:
            width = int(config["WIDTH"])
            height = int(config["HEIGHT"])
            x, y = config["ENTRY"].split(",", 1)
            entry = (int(x), int(y))
            x, y = config["EXIT"].split(",", 1)
            exit_pos = (int(x), int(y))
            output_file = config["OUTPUT_FILE"]
            perfect = config.get("PERFECT", "False").lower() == "true"
            if "SEED" in config:
                seed = int(config["SEED"])
            else:
                seed = randbits(8)
        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid value in configuration: {e}")
        return cls(width, height, entry, exit_pos, output_file, perfect, seed)
