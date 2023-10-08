import Migrate


if __name__ == "__main__":

    import logging
    import sys

    log = logging.getLogger("EHRQC")
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    log.info("Parsing command line arguments")

    Migrate.omopToFhir(
        entity="Organization",
        sqlFilePath="migrate/sql/Organization.sql",
        xmlTemplatePath="migrate/templates/Organization.json",
        mapping={"name":"organization_name"}
        )
