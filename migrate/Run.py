import migrate.Migrate as Migrate


if __name__ == "__main__":

    from migrate.config import RunConfig as RunConfig

    import logging
    import sys

    log = logging.getLogger("EHRQC")
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    for config in RunConfig.run_config:
        if config['type'] == 'migrate':
            Migrate.omopToFhir(
                entity=config['entity'],
                sqlFilePath=config['sqlFilePath'],
                xmlTemplatePath=config['xmlTemplatePath'],
                mapping=config['xml_sql_mapping'],
                )
        elif config['type'] == 'execute':
            config['function']()
