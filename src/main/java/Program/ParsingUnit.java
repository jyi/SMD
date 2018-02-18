package Program;

import org.antlr.v4.runtime.Token;
import org.apache.commons.collections4.CollectionUtils;
import org.jgrapht.graph.DefaultEdge;
import org.jgrapht.graph.SimpleDirectedGraph;

import java.util.*;

public class ParsingUnit {
    public static LinkedList<String> classes = new LinkedList<>();
    public static LinkedList<Token> tokens = new LinkedList<>();

    public static Map<String, Integer> wmcMap = new HashMap<>();
    public static Map<String, HashSet<String>> cboMap = new HashMap<>(); // <ClassName, <Set of coupled classes>>
    public static Map<String, Integer> rfcMap = new HashMap<>();

    // Temp map for LCOM computing Map<ClassName, Map<MethodName, List<UsedVariables>>>
    public static Map<String, Map<String, LinkedList<String>>> lcomMap = new HashMap<>();

    public static Map<String, Set<String>> classVariables= new HashMap<>();
    public static Map<String, Integer> cboResult = new HashMap<>();
    public static Map<String, Integer> lcomResult = new HashMap<>();

    public static SimpleDirectedGraph<String, DefaultEdge> couplingClassesGraph = new SimpleDirectedGraph<>(DefaultEdge.class);

    public static void processMapsValues(){
        updateCboCount();
        ParsingUnit.updateRfc();
        ParsingUnit.removeRedundantFieldsFromUsedVarsMap();
        ParsingUnit.computeLcom();
    }

    public static void printCboMap(){
        System.out.println("\n ----- Cbo Map ------- ");
        couplingClassesGraph.vertexSet().forEach(vertex -> {
            System.out.print(vertex + " : ");
            couplingClassesGraph.edgesOf(vertex).forEach(edge -> System.out.print(edge + ", "));
            System.out.println();
        });
    }

    public static void printRfcMap(){
        System.out.println("\n ----- Rfc Map ------");
        rfcMap.forEach((k,v) -> System.out.println(k + " : " + v));
        System.out.println();
    }

    private static void updateCboCount(){
        couplingClassesGraph.vertexSet().forEach(vertex -> {
            cboResult.put(vertex, couplingClassesGraph.degreeOf(vertex));
        });
    }

    // Add WMC values to the RFC.
    private static void updateRfc(){
        wmcMap.remove("");

        wmcMap.forEach((className, wmc) -> {
            if(!rfcMap.containsKey(className)){
                rfcMap.put(className, 0);
                return;
            }

            int rfc = rfcMap.get(className) + wmc;
            rfcMap.put(className, rfc);
        });
    }

    private static void removeRedundantFieldsFromUsedVarsMap(){
        classVariables.forEach((className, vars)-> {
            Map<String, LinkedList<String>> methodsWithNotFilteredVariables = lcomMap.get(className);

            if (methodsWithNotFilteredVariables == null) {
                return;
            }

            for (Map.Entry<String, LinkedList<String>> entry : methodsWithNotFilteredVariables.entrySet()) {
                LinkedList<String> notFilteredVariables = entry.getValue();
                notFilteredVariables.removeIf(var -> !vars.contains(var));

                entry.setValue(notFilteredVariables);
            }

        });
    }

    private static void computeLcom(){
        lcomMap.forEach((className, methods) ->{
            int P = 0, Q = 0;

            ArrayList<String> keys = new ArrayList<>(methods.keySet());

            for(int i = 0; i < keys.size() - 1; i++){
                for(int j = i + 1; j < keys.size(); j++){

                    // Intersection of two lists.
                    /*Map<String, LinkedList<String>> clonedMethods = methods.get(keys.get(i)).clone();

                    methods.get(keys.get(i)).retainAll(methods.get(keys.get(j)));*/



                    if(CollectionUtils.containsAny(methods.get(keys.get(i)), methods.get(keys.get(j)))){
                        Q++;
                    }
                    else {
                        P++;
                    }
                }
            }

            int lcom = P - Q;
            if(lcom < 0) lcom = 0;

            lcomResult.put(className, lcom);

        });
    }


}