from langchain_ollama import OllamaLLM

class SCsGenerator:
    def __init__(self, model_name, ctx):
        self.llm = OllamaLLM(model=model_name, temperature=0.0, num_ctx=ctx)

    def text_to_scs(self, text):
        prompt = f"""
        Ты — интеллектуальный анализатор текста, эксперт в OSTIS. Твоя задача - выделить из текста все понятия(сущности, объекты, термины, явления) и преобразовать их в scs-код.

        Правила:
        1. Абсолютные понятия(предметы, явления) начинаются с concept_
        2. Относительные понятия(связи между абсолютными) начинаются с nrel_
        3. Каждому понятию нужно присвоить основной идентификатор: 
           concept_term=>nrel_main_idtf: 
                   [название на русском](*<-lang_ru;;*);
                   [название на английском](*<-lang_eng;;*);;
        4. Для абсолютных понятий выделить иерархию: subclass<=nrel_inclusion:superclass;;
        5. Каждому понятию дать определение: concept_term=>nrel_definition: [текст](*<-lang_ru;;*);;
        6. Относительному понятию выделить его домены(связывающие классы):
           nrel_rel
           =>nrel_first_domain: concept_term1;
           =>nrel_second_domain: concept_term2;;
        7. Каждому понятию выделить экземпляр: concept_term->example;;
        8. Конструкции, относящиеся к понятию, разделяются точкой с запятой. В конце последней конструкции, применимой к ОДНОМУ понятию(а не в самом конце всего текста), ставится двойная точка с запятой(;;)

        Пример правильного scs для абсолютного понятия пирамида и относительного понятия основание:
        concept_pyramid 
        =>nrel_main_idtf: [пирамида](*<-lang_ru;;*);
                          [pyramid](*<-lang_eng;;*);
        <=nrel_inclusion: concept_polyhedron;
        =>nrel_definition: [многогранник с основанием-многоугольником](*<-lang_ru;;*);
        ->ABCD;;

        nrel_base
        =>nrel_main_idtf: [основание](*<-lang_ru;;*);
                          [base](*<-lang_eng;;*);
        =>nrel_definition: [грань, которой не принадлежит вершина](*<-lang_ru;;*);
        =>nrel_first_domain: concept_pyramid;
        =>nrel_second_domain: concept_polygon;
        ->ABC;;

        ТЕКСТ: {text}   
        
        Проанализируй правила и примеры и дай сгенерированный scs-код.
        """
        return self.llm.invoke(prompt)
