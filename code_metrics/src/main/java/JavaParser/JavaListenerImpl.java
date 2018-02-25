package JavaParser;

import Program.ParsingUnit;
import Utils.StringProcesser;
import org.jgrapht.Graph;
import org.jgrapht.graph.DefaultEdge;
import org.jgrapht.graph.SimpleDirectedGraph;
import org.jgrapht.traverse.DepthFirstIterator;

import java.util.*;

public class JavaListenerImpl extends JavaBaseListener {
    private static int _instanceNum = 0; // TODO: remove on release
    private int _wmc = 0;  // TODO: remove _wmc. It already has been calculated using modified grammar
    private boolean _isInterface = false; // If interface or Enum --> ignore and skip it. Program supposed to collect only class metrics

    private String _className = "";
    private String _currentMethod = "";
    private String _package = "";

    private boolean enteredClassBodyDeclaration = false;
    private boolean enteredMethodDeclaration = false;
    private boolean enteredFieldDeclaration = false;

    private static SimpleDirectedGraph<String, DefaultEdge> _inheritanceGraph = new SimpleDirectedGraph<>(DefaultEdge.class);
    private Set<String> _methodsSet = new HashSet<>();
    private static Set<String> _classes = new HashSet<>();


    public JavaListenerImpl(){
        _instanceNum++;
    }

    @Override
    public void enterPackageDeclaration(JavaParser.PackageDeclarationContext ctx) {
        _package = ctx.getText().replaceFirst("^package", "").replaceFirst(";", ".");
    }

    @Override
    public void enterInterfaceDeclaration(JavaParser.InterfaceDeclarationContext ctx) {
        _isInterface = true;
    }

    @Override
    public void enterEnumDeclaration(JavaParser.EnumDeclarationContext ctx) {
        _isInterface = true;
    }

    @Override
    public void enterClassDeclaration(JavaParser.ClassDeclarationContext ctx) {
        _className = _package + ctx.IDENTIFIER().toString();
        _classes.add(_className);

        /*
         * From grammar file
         * */
        ParsingUnit.tokens.add(ctx.IDENTIFIER().getSymbol());
        ParsingUnit.cboMap.put(_className, new HashSet<>());
        //ParsingUnit.rfcMap.put(_className, 0);
        ParsingUnit.wmcMap.put(_className, 0);


        // Class hierarchy graph
        _inheritanceGraph.addVertex(_className);

        ParsingUnit.couplingClassesGraph.addVertex(_className);
        ParsingUnit.classVariables.put(_className, new HashSet<>());
        ParsingUnit.lcomMap.put(_className, new HashMap<>());
        //_inheritanceGraph


        if(ctx.typeType() != null){
            String parent = ctx.typeType().getText();
            _inheritanceGraph.addVertex(parent);
            if(!_className.equals(parent))
                _inheritanceGraph.addEdge(_className, parent);
        }

    }

    @Override
    public void enterClassOrInterfaceType(JavaParser.ClassOrInterfaceTypeContext ctx) {
        if(!"".equals(_className)){
            HashSet<String> set3 = ParsingUnit.cboMap.get(_className);
            set3.add(ctx.i2.getText());
            ParsingUnit.cboMap.put(_className, set3);
        }
    }

    @Override
    public void enterClassBodyDeclaration(JavaParser.ClassBodyDeclarationContext ctx) {
        enteredClassBodyDeclaration = true;
    }


    // CBO computing
    @Override
    public void enterTypeType(JavaParser.TypeTypeContext ctx) {
        if (_isInterface || _className.equals("") || ctx.classOrInterfaceType() == null) {
            return;
        }

        String enteredType = ctx.classOrInterfaceType().i2.getText();
        if(ParsingUnit.classes.contains(enteredType) && !_className.equals(enteredType)){
            ParsingUnit.couplingClassesGraph.addVertex(enteredType);
            ParsingUnit.couplingClassesGraph.addEdge(_className, enteredType);
        }
    }

    @Override
    public void enterParExpression(JavaParser.ParExpressionContext ctx) {
        super.enterParExpression(ctx);
    }

    @Override
    public void enterExpressionList(JavaParser.ExpressionListContext ctx) {
        super.enterExpressionList(ctx);
    }

    @Override
    public void exitClassBodyDeclaration(JavaParser.ClassBodyDeclarationContext ctx) {
        enteredClassBodyDeclaration = false;
    }


    @Override
    public void enterMethodDeclaration(JavaParser.MethodDeclarationContext ctx) {
        if(_isInterface)
            return;

        _wmc++;
        int wmc = ParsingUnit.wmcMap.getOrDefault(_className, -100001) + 1;
        ParsingUnit.wmcMap.put(_className, wmc);

        enteredMethodDeclaration = true;
        _currentMethod = ctx.IDENTIFIER().getText();

        /*
        * If Set of methods of the class contains current method, it means this is overloaded method. Then,
        * Put the signature(name + params) of the method into _currentMethod
        * */
        if(_methodsSet.contains(_currentMethod))
           // _currentMethod = StringProcesser.getMethodSignature(ctx);
            _currentMethod = ctx.formalParameters().getText();
        else
            _methodsSet.add(_currentMethod);

        // LCOM filling map with methods
        Map<String, LinkedList<String>> methodAndUsedVariables = ParsingUnit.lcomMap.get(_className);
        methodAndUsedVariables.put(_currentMethod, new LinkedList<>());
    }

    @Override
    public void exitMethodDeclaration(JavaParser.MethodDeclarationContext ctx) {
        _currentMethod = "";
        enteredMethodDeclaration = false;
    }


    // LCOM computing
    @Override
    public void enterPrimary(JavaParser.PrimaryContext ctx) {
        if (_isInterface || _className.equals("") || !enteredMethodDeclaration || ctx.IDENTIFIER() == null)
            return;

        Map<String, LinkedList<String>> methodAndUsedVariables = ParsingUnit.lcomMap.get(_className);
        LinkedList<String> usedVariables = methodAndUsedVariables.getOrDefault(_currentMethod, new LinkedList<>());
        usedVariables.add(ctx.IDENTIFIER().getText());

        methodAndUsedVariables.put(_currentMethod, usedVariables);
        ParsingUnit.lcomMap.put(_className, methodAndUsedVariables);

    }

    @Override
    public void enterFieldDeclaration(JavaParser.FieldDeclarationContext ctx) {
        enteredFieldDeclaration = true;
    }

    @Override
    public void exitFieldDeclaration(JavaParser.FieldDeclarationContext ctx) {
        enteredFieldDeclaration = false;
    }

    @Override
    public void enterVariableDeclaratorId(JavaParser.VariableDeclaratorIdContext ctx) {
        if(_isInterface || !enteredFieldDeclaration || ctx.IDENTIFIER() == null) return;

        Set<String> variables = ParsingUnit.classVariables.getOrDefault(_className, new HashSet<>());
        variables.add(ctx.IDENTIFIER().getText());
        ParsingUnit.classVariables.put(_className, variables);
    }

    @Override
    public void exitVariableDeclaratorId(JavaParser.VariableDeclaratorIdContext ctx) {
        super.exitVariableDeclaratorId(ctx);
    }

    @Override
    public void enterConstructorDeclaration(JavaParser.ConstructorDeclarationContext ctx) {
        _wmc++;
        enteredMethodDeclaration = true;
        _currentMethod = _className;

        int wmc = ParsingUnit.wmcMap.getOrDefault(_className, -100001) + 1;
        ParsingUnit.wmcMap.put(_className, wmc);
    }

    @Override
    public void exitConstructorDeclaration(JavaParser.ConstructorDeclarationContext ctx) {
        enteredMethodDeclaration = false;
        _currentMethod = "";
    }

    public int getWmc() {
        return _wmc;
    }

    public boolean isInterfaceOrEnum() {
        return _isInterface;
    }


    public static void replaceShortClassNamesWithFullyQualified(){
        if(_classes.isEmpty())
            return;

        /*for(String cl : _classes){
            for(String vertex : _inheritanceGraph.vertexSet()){
                if(cl.equals(vertex))
                    continue;

                if(StringProcesser.getShortClassName(cl)
                        .equals(vertex)){
                    replaceVertex(_inheritanceGraph, vertex, cl);
                }
            }
        }*/

        for(String cl : _classes){
            LinkedList<String> vertices = new LinkedList<>(_inheritanceGraph.vertexSet());

            for(int i = 0; i < vertices.size(); i++){


                if(cl.equals(vertices.get(i)))
                    continue;

                if(StringProcesser.getShortClassName(cl)
                        .equals(vertices.get(i))){
                    replaceVertex(_inheritanceGraph, vertices.get(i), cl);
                }
            }
        }

    }

    private static <V, E> void replaceVertex(Graph<V, E> graph, V vertex, V replace) {
       /* for (E edge : graph.outgoingEdgesOf(vertex)){

            throw new UnsupportedOperationException("Shouldn't be executed. Vertex " +  vertex + " replace " + replace);
        }*/


        for (E edge : graph.incomingEdgesOf(vertex)){
            V src = graph.getEdgeSource(edge);
            V dst = graph.getEdgeTarget(edge);
           // graph.addEdge(graph.getEdgeSource(edge), replace, edge);
            graph.addEdge(src, replace);
        }

        graph.removeVertex(vertex);

       // graph.incomingEdgesOf(v)
    }

    public static int getDit(String className){
        if(!_inheritanceGraph.containsVertex(className))
            return -1;
        final int[] dit = {0};

        DepthFirstIterator<String, DefaultEdge> dfi = new DepthFirstIterator<>(_inheritanceGraph, className);
        dfi.forEachRemaining(x -> dit[0]++);
        return dit[0];
    }

    public static int getNoc(String className){
        if(!_inheritanceGraph.containsVertex(className))
            return -1;

        final int[] noc = {0};
        _inheritanceGraph.incomingEdgesOf(className).forEach(x -> noc[0]++);
        return noc[0];
    }

    public String get_className() {
        return _className;
    }
}