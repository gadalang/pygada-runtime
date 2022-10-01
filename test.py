import pygada_runtime

with pygada_runtime.run(
    {
        "name": "test",
        "inputs": [
            {"name": "a", "value": 1, "type": "int"},
            {"name": "b", "value": 2, "type": "int"},
        ],
        "outputs": "max",
        "steps": [{"name": "max", "id": "max"}],
    },
    gada_bin="F:/gadalang/venv/Scripts/gada",
) as process:
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)
