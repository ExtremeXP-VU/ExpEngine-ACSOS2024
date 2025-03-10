/*
 * generated by Xtext 2.32.0
 */
package exp.engine.dsl.scoping

import org.eclipse.emf.ecore.EObject
import org.eclipse.emf.ecore.EReference
import org.eclipse.xtext.scoping.IScope
import exp.engine.dsl.expLang.TaskConfiguration
import exp.engine.dsl.expLang.AssembledWorkflow
import exp.engine.dsl.expLang.ExpLangPackage
import org.eclipse.xtext.scoping.Scopes
import exp.engine.dsl.expLang.ESpaceTaskConfiguration
import exp.engine.dsl.expLang.Space
import exp.engine.dsl.expLang.OrdinaryFlow
import exp.engine.dsl.expLang.Experiment
import exp.engine.dsl.expLang.EventOrSpace
import java.util.ArrayList

/**
 * This class contains custom scoping description.
 * 
 * See https://www.eclipse.org/Xtext/documentation/303_runtime_concepts.html#scoping
 * on how and when to use it.
 */
class ExpLangScopeProvider extends AbstractExpLangScopeProvider {

    
	 override IScope getScope(EObject context, EReference reference){
	 	
	 	if (context instanceof TaskConfiguration){
	 		val container = context.eContainer
	 		if (container instanceof AssembledWorkflow){
	 			if (reference == ExpLangPackage.Literals.TASK_CONFIGURATION__ALIAS){
	 				return Scopes.scopeFor(container.parent_workflow.tasks)
	 			}
	 		}
	 	}
	 	
	 	if (context instanceof ESpaceTaskConfiguration){
	 		val container = context.eContainer
	 		if (container instanceof Space){
	 			if (reference == ExpLangPackage.Literals.ESPACE_TASK_CONFIGURATION__TASK){
	 				val tasks = newArrayList
	 				container.assembled_workflow.tasks.forEach[
	 					e |
	 					tasks += e.alias
	 				]
	 				return Scopes.scopeFor(tasks)
	 			}
	 		}
	 	}
	 	
	 	if (context instanceof OrdinaryFlow){
	 		if (reference == ExpLangPackage.Literals.ORDINARY_FLOW__ORIGIN){
	 			val eventOrSpaces = new ArrayList<EventOrSpace>()
	 			var experiment = context.eContainer.eContainer
	 			if (experiment instanceof Experiment){
					println (experiment.spaces)
	 				eventOrSpaces += experiment.spaces
	 				eventOrSpaces += experiment.events
	 				return Scopes.scopeFor(eventOrSpaces)
	 			}
	 		}
	 	}
        
        return super.getScope(context, reference)
    }
}
