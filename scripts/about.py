
import streamlit as st

class AboutPage:
    def render(self, conn=None):
        st.header("About the Creator")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150) # Placeholder or user avatar
            st.markdown("### K. Natrajan")
            st.caption("Lead Automation Engineer")
            st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/)")

        with col2:
            st.info(
                """
                **With over 7.6 years of experience in the software industry**, I specialize in building robust automation frameworks that ensure data integrity and system reliability. 
                My career has been defined by a transition from manual validation to architecting sophisticated automation pipelines for global leaders like Mindtree and RNTBCI.
                """
            )
            
            st.markdown("#### 🚀 Industry Expertise")
            st.write("I have a proven track record in Banking and Supply Chain Finance, developing solutions that automate end-to-end office software for wholesale petroleum and petroleum-related financial transactions.")
            
            st.markdown("#### 💻 Technical Core")
            st.write("My expertise lies in **Selenium with Java**, **API Automation (Rest Assured)**, and **SQL-based data validation**.")
            
            st.markdown("#### 🏆 Strategic Leadership")
            st.write("Beyond writing scripts, I lead QA teams, mentor junior engineers, and manage CI/CD execution via Jenkins to ensure **95% automation coverage** for production releases.")
            
            st.markdown("#### 🎓 Education")
            st.write("I hold a **Master of Computer Applications (MCA)**, reinforcing my practical experience with deep theoretical knowledge.")
