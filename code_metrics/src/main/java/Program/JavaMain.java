package Program;

import JavaParser.JavaLexer;
import JavaParser.JavaListenerImpl;
import JavaParser.JavaParser;
import Utils.LinuxPathConstants;
import Utils.RuntimeMeasurement;
import org.antlr.v4.runtime.ANTLRFileStream;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.ParseTreeWalker;
import org.apache.commons.io.FilenameUtils;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;

public class JavaMain {
    private static String path;
    private static String pathToOutput = "./";

    public static Map<String, JavaListenerImpl> classes = new TreeMap<>();

    public static void main(String[] args) throws IOException {
        RuntimeMeasurement runtime = new RuntimeMeasurement();
        runtime.logStartingTimeAndMemory();

        if(args == null || args.length == 0){
            System.out.println("Error. Path to a project must be provided.");
            return;
        }

        path = args[0];

        if(args.length == 2){
            pathToOutput = args[1];
        }

        File file = new File(path);
        createListOfClasses(file);
        System.out.println();

        listFilesForFolderAndComputeMetrics(file);

        ParsingUnit.processMapsValues();
        JavaListenerImpl.replaceShortClassNamesWithFullyQualified();

        runtime.logFinishingTimeAndMemory();

        System.out.printf("Elapsed time: %1$.3f sec\n", runtime.getTimeSpentInSeconds());
        System.out.printf("Memory used:  %1$.3f Mb\n", runtime.getMemorySpentInMegabytes());

        writeToCSV();

        System.out.println("Successfully completed.");
    }


    private static void listFilesForFolderAndComputeMetrics(final File fileOrDirectory) throws IOException {
        int k = 0;
        for (final File fileEntry : Objects.requireNonNull(fileOrDirectory.listFiles())) {
                if(fileEntry.isDirectory())
                    listFilesForFolderAndComputeMetrics(fileEntry);

                String fileName = fileEntry.getName();
                if(FilenameUtils.getExtension(fileName).equals("java")){


                    JavaListenerImpl listener = getListener(fileEntry.getPath());

                    if(listener.isInterfaceOrEnum())
                        continue;
                    classes.put(listener.get_className(), listener);
                }
        }
    }


    private static void createListOfClasses(final File fileOrDirectory){
        for(final File fileEntry : Objects.requireNonNull(fileOrDirectory.listFiles())){
            if(fileEntry.isDirectory()) {
                createListOfClasses(fileEntry);
            }


            String fileName = fileEntry.getName();
            if(FilenameUtils.getExtension(fileName).equals("java")){
                ParsingUnit.classes.add(FilenameUtils.removeExtension(fileName));
            }

        }
    }

    private static JavaListenerImpl getListener(String file) throws IOException {
        JavaLexer lexer = new JavaLexer(new ANTLRFileStream(file));
        JavaParser parser = new JavaParser(new CommonTokenStream(lexer));

        ParseTree tree = parser.compilationUnit();
        ParseTreeWalker walker = new ParseTreeWalker();
        JavaListenerImpl listener = new JavaListenerImpl();

        walker.walk(listener, tree);

        return listener;
    }

    private static void writeToCSV(){
        BufferedWriter writer = null;
        try {
            File file = new File(pathToOutput + path.substring(FilenameUtils.indexOfLastSeparator(path)+1) + ".csv");

            writer = new BufferedWriter(new FileWriter((file.getAbsoluteFile())));
            writer.write("classname,wmc,dit,noc,cbo,rfc,lcom");
            writer.newLine();
            for(Map.Entry<String, JavaListenerImpl> entry : classes.entrySet()){
                String key = entry.getKey();
                writer.write(
                        key + ","
                        + entry.getValue().getWmc() + ","
                        + JavaListenerImpl.getDit(key) + ","
                        + JavaListenerImpl.getNoc(key) + ","
                        + ParsingUnit.cboResult.get(key) + ","
                        + ParsingUnit.rfcMap.get(key) + ","
                        + ParsingUnit.lcomResult.get(entry.getKey())
                );

                writer.newLine();
            }

            //WRITING
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if (writer != null) writer.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
