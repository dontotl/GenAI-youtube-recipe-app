import os
import openai
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
 
OPENAI_API_key='xxxxxxxxxxxxxxxxxxxx'
openai.api_key=OPENAI_API_key

def get_transcript(youtube_url):
    video_id = youtube_url.split("v=")[-1]
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    try:
        transcript = transcript_list.find_manually_created_transcript()
        language_code = transcript.language_code   
    except:
        try:
            generated_transcripts = [trans for trans in transcript_list if trans.is_generated]
            transcript = generated_transcripts[0]
            language_code = transcript.language_code   
        except:
            raise Exception("No suitable transcript found.")

    full_transcript = " ".join([part['text'] for part in transcript.fetch()])
    return full_transcript, language_code  # Return both the transcript and detected language

def summarize_with_langchain_and_openai(transcript, language_code, model_name='gpt-3.5-turbo'):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    texts = text_splitter.split_text(transcript)
    text_to_summarize = " ".join(texts[:4]) # Adjust this as needed

    system_prompt = '쉬운말투로 요리와 레시피를 정리해줘.'
    prompt = f'''요리를 하기위한 재료와 레시피를 한글로 정리해줘.
    Text: {text_to_summarize}

    Add a title to the summary in {language_code}. 
    Include an INTRODUCTION, BULLET POINTS if possible, and a CONCLUSION in {language_code}.'''

    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': prompt}
        ],
        temperature=1
    )
    
    return response['choices'][0]['message']['content']

def main():
    st.title('YouTube 레시피 요약')
    link = st.text_input('YouTube 링크를 넣으면 레시피를 요약해 줍니다:')

    if st.button('Start'):
        if link:
            try:
                progress = st.progress(0)
                status_text = st.empty()

                status_text.text('스크립트 추출 중...')
                progress.progress(25)

                transcript, language_code = get_transcript(link)

                status_text.text(f'요약 생성 중...')
                progress.progress(75)

                model_name = 'gpt-3.5-turbo'
                summary = summarize_with_langchain_and_openai(transcript, 'korean', model_name)

                status_text.text('레시피 요약:')
                st.markdown(summary)
                progress.progress(100)
            except Exception as e:
                st.write(str(e))
        else:
            st.write('YouTube 링크를 넣으세요.')

if __name__ == "__main__":
    main()
