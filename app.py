import streamlit as st

st.set_page_config(page_title="OmniLearn 2.0", page_icon="⚡", layout="wide")

st.title("⚡ OmniLearn 2.0: Active Study Engine")
st.caption("Your information organizes itself. Your AI tutor tests you on what you don't know.")

# Create the 3 main tabs for the app
tab1, tab2, tab3 = st.tabs(["📊 Capture Feed", "🕸️ Knowledge Graph", "🎯 Gap Analysis & Quiz"])

with tab1:
    st.header("Recent Captures")
    st.success("⚡ Live Capture Active (Global Hotkey: Ctrl + Shift + O)")
    st.text_input("🔍 Search captured notes...", placeholder="Try typing 'What is on the midterm?'")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Physics - Newton's Second Law")
        st.json({
            "subject": "Physics",
            "topic": "Mechanics",
            "concept": "Newton's Second Law",
            "formula": "F = ma",
            "source": "Lecture Slide"
        })
    with col2:
        st.subheader("Physics Midterm Announcement")
        st.json({
            "subject": "Physics",
            "topic": "Exam Format",
            "date": "This Friday",
            "topics_covered": "Chapters 1-4",
            "source": "WhatsApp Group"
        })

with tab2:
    st.header("Semantic Knowledge Graph")
    st.write("Visual representation of concepts extracted from your captured screenshots.")
    
    # Graphviz DOT string for rendering connected nodes
    graph_code = '''
    digraph KnowledgeGraph {
        graph [rankdir=TB, bgcolor="transparent"]
        node [fontname="Arial", shape=box, style="filled,rounded", color="#333333"]
        edge [fontname="Arial", color="#888888"]

        // Central Root Node
        Physics [label="PHYSICS\n(Root Subject)", fillcolor="#4CAF50", fontcolor="white", fontsize=16]

        // Topic Nodes
        Mechanics [label="Mechanics", fillcolor="#2196F3", fontcolor="white", fontsize=14]
        Kinematics [label="Kinematics", fillcolor="#2196F3", fontcolor="white", fontsize=14]

        // Concept Nodes
        Newton [label="Newton's 2nd Law\n(F = ma)", fillcolor="#E91E63", fontcolor="white"]
        Gravity [label="Gravity", fillcolor="#E91E63", fontcolor="white"]
        Pulley [label="Pulley System\nEquilibrium", fillcolor="#E91E63", fontcolor="white"]

        // AI Knowledge Gap Node (Dashed outline & warning color)
        Gap_Momentum [label="⚠️ Momentum\n(Missing Screenshot Gap)", fillcolor="#FF9800", fontcolor="white", style="filled,dashed"]

        // Relationships
        Physics -> Mechanics
        Physics -> Kinematics
        
        Mechanics -> Newton
        Mechanics -> Gravity
        Mechanics -> Pulley
        Mechanics -> Gap_Momentum [style=dashed, label="Missing Concept"]
    }
    '''
    
    st.graphviz_chart(graph_code)

with tab3:
    st.header("AI Gap Analysis & Active Recall")
    st.warning("⚠️ AI Detected 1 Missing Syllabus Topic: **Momentum**")
    
    if st.button("⚡ Generate Active Recall Quiz"):
        st.subheader("Question 1 (Based on your notes):")
        st.write("According to Newton's Second Law ($F = ma$), if the net force acting on an object is doubled while its mass stays constant, what happens to its acceleration?")
        st.radio("Select your answer:", [
            "It stays the same",
            "It doubles",
            "It is halved",
            "It quadruples"
        ])
        if st.button("Submit Answer"):
            st.success("Correct! Acceleration is directly proportional to force ($a = F/m$).")
            
