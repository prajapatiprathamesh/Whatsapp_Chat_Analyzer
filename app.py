import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from PIL import Image

im = Image.open("what.ico")
st.set_page_config(
    page_title="WhatsApp Analysis",
    page_icon=im,
    layout="wide",
)
st.sidebar.title('WhatsApp Chat Analysis')
col1, col2, col3, col4 = st.sidebar.columns([1, 2, 2, 1])
with col2:
    st.image('https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/WhatsApp.svg/479px-WhatsApp.svg.png', width=90)
with col3:
    st.image('analy.png', width=90)

st.sidebar.caption(
    'This application lets you analyze Whatsapp conversations in a very comprehensive manner, with charts, metrics, '
    'and other forms of analysis.')
st.title('WhatsApp Chat Analyzer')
st.markdown('Developed with Streamlit, Developed by Prathamesh')

with st.expander('See!!.. How it works?'):
    st.subheader('Steps to Analyze:')
    st.markdown(
        '1. Export the chat by going to WhatsApp on your phone, opening the chat, clicking on the three dots, '
        'selecting "More," and then choosing "Export Chat" without media. Save the file to your desired location.')
    st.markdown(
        '2. Browse or drag and drop the chat file.')
    st.markdown('3. Select a user or group to analyze, or leave the default setting of "All" to analyze for all users.')
    st.markdown('4. Click the "Show Analysis" button.')
    st.markdown(
        '5. Enable "Wide mode" for a better viewing experience in settings, or close the sidebar on mobile for improved'
        ' view.')
    st.markdown(
        '6. To analyze for a single user, select their name from the dropdown and click "Show Analysis" again.')

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:  # Check if 'group_notification' exists
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Select UserName", user_list)

    
    if selected_user != 'Overall':
        st.subheader(f'Selected Users: {selected_user}')
    else:
        st.subheader('All Users')

    if st.sidebar.button("Show Analysis"):

        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # st.title("Weekly Activity Map")
        # user_heatmap = helper.activity_heatmap(selected_user, df)
        # fig, ax = plt.subplots()
        # ax = sns.heatmap(user_heatmap)
        # st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)

        if user_heatmap is not None:
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)
        else:
            st.write("No activity data available to generate the heatmap.")

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("Wordcloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # most common words
        most_common_df = helper.most_common_words(selected_user, df)

        fig, ax = plt.subplots()

        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')

        st.title('Most common words')
        st.pyplot(fig)

        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            fig = px.pie(emoji_df, values='count', names='emoji')
            fig.update_traces(text= emoji_df['emoji'], hovertemplate='%{label}: %{value}<br>%{percent}%')
            st.plotly_chart(fig)

        #     fig,ax = plt.subplots()
        #     ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(),autopct="%0.2f")
        #     st.pyplot(fig)
