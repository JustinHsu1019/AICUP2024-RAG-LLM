import textwrap

import openai

import utils.config_log as config_log

config, logger, CONFIG_PATH = config_log.setup_config_and_logging()
config.read(CONFIG_PATH)


def gpt_template(prompt, output_way='json'):
    openai.api_key = config.get('OpenAI', 'api_key')

    userprompt = textwrap.dedent(
        f"""
        {prompt}
    """
    )

    response = openai.ChatCompletion.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': '使用繁體中文回答'},
            {'role': 'user', 'content': userprompt},
        ],
    )

    return response.choices[0].message['content']


def main():
    """範例: GPT 模板使用"""
    # import utils.gpt_integration as gpt_call
    # gpt_call.gpt_template()
    print(gpt_template('問題: 太陽系有哪些行星？請用 json 格式回傳，{"回傳內容": "_回答_"}'))


if __name__ == '__main__':
    main()
