from bpmn_python.bpmn_diagram_rep import BpmnDiagramGraph

graph = BpmnDiagramGraph()
process_id = graph.create_new_diagram_graph(diagram_name='Example')
start = graph.add_start_event_to_diagram(process_id) # 'start', name='Start')
task = graph.add_task_to_diagram(process_id, 'task1') #name='Task 1')
end = graph.add_end_event_to_diagram(process_id, 'end') # name='End')
graph.add_sequence_flow_to_diagram(process_id, start, task, 'flow1')
graph.add_sequence_flow_to_diagram(process_id, task, end, 'flow2')
graph.export_xml_file('.', 'example.bpmn')
