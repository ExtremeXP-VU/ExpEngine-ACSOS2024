# EXP Language Server

Required software:
- [Maven](https://maven.apache.org/)
- [Java](https://www.java.com/en/download/)

In order to run the language server, first create the DSL artefact using `mvn`:

```bash
cd exp.engine.dsl.parent
mvn install
```

Now, create the language server:

```bash
cd exp.engine.dsl.parent/exp.engine.dsl.ide
mvn install -Plang-server
```

Run the language server as:
```bash
cd exp.engine.dsl.parent/exp.engine.dsl.ide/target
java -jar exp.engine.dsl.ide-1.0.0-SNAPSHOT-ls.jar
```

After running the language server, the following message should be shown:

```
Welcome to Experiment LSP version 4.0 - Resolved
```
