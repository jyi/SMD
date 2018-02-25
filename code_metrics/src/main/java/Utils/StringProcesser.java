package Utils;

import JavaParser.JavaParser;

/**
 * Created by gab on 26.Jan.2018
 */
public class StringProcesser {
    public static String getMethodSignature(JavaParser.MethodDeclarationContext ctx){
        StringBuilder sb = new StringBuilder(ctx.IDENTIFIER().getText());
        if(ctx.formalParameters().formalParameterList() != null){
            sb.append("(");
            ctx.formalParameters().formalParameterList()
                    .formalParameter().forEach(param -> sb.append(param.typeType().getText()).append(", "));
            sb.replace(sb.lastIndexOf(", "), sb.length(), ")");
        }
        return sb.toString();
    }

    public static String getShortClassName(String className){
        return className.substring(className.lastIndexOf('.') + 1);
    }

    public static String getLongestString(String s1, String s2){
        return s1.length() >= s2.length() ? s1 : s2;
    }

    public static String getShortestString(String s1, String s2){
        return s1.length() < s2.length() ? s1 : s2;
    }
}
