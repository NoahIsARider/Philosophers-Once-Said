import customtkinter as ctk
from openai import OpenAI
import threading
import json
import os
from dotenv import load_dotenv
from agents import DeleuzeAgent, SpinozaAgent, RanciereAgent, FoucaultAgent, ZizekAgent
from search import WebSearcher

# Load environment variables from .env file
load_dotenv()

class PhilosopherChat:
    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv('MODELSCOPE_API_BASE'),
            api_key=os.getenv('MODELSCOPE_API_KEY')
        )
        
        # 初始化网络搜索器
        self.searcher = WebSearcher()
        
        # 使用从agents模块导入的哲学家类
        self.philosopher_agents = {
            DeleuzeAgent.name: DeleuzeAgent,
            SpinozaAgent.name: SpinozaAgent,
            RanciereAgent.name: RanciereAgent,
            FoucaultAgent.name: FoucaultAgent,
            ZizekAgent.name: ZizekAgent
        }
        
        # 创建哲学家名称到提示的映射
        self.philosophers = {}
        for name, agent_class in self.philosopher_agents.items():
            self.philosophers[name] = agent_class.get_prompt()
        
        # 为每个哲学家创建对话历史
        self.conversation_history = {}
        for name in self.philosopher_agents.keys():
            self.conversation_history[name] = []
        
        self.setup_gui()
        
    def setup_gui(self):
        self.window = ctk.CTk()
        self.window.title("Philosopher Once Said...")
        self.window.geometry("800x600")
        
        # 左侧选择框
        left_frame = ctk.CTkFrame(self.window, width=200)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(left_frame, text="选择对话哲学家").pack(pady=10)
        
        self.philosopher_vars = {}
        for philosopher in self.philosopher_agents.keys():
            var = ctk.BooleanVar()
            self.philosopher_vars[philosopher] = var
            ctk.CTkCheckBox(left_frame, text=philosopher, variable=var).pack(pady=5)
        
        # 添加搜索功能
        search_frame = ctk.CTkFrame(left_frame)
        search_frame.pack(fill="x", pady=20, padx=5)
        
        ctk.CTkLabel(search_frame, text="网络搜索").pack(pady=5)
        
        self.search_input = ctk.CTkEntry(search_frame, placeholder_text="输入搜索关键词")
        self.search_input.pack(fill="x", pady=5)
        
        search_button = ctk.CTkButton(search_frame, text="搜索", command=self.perform_search)
        search_button.pack(fill="x", pady=5)
        
        # 右侧对话框
        right_frame = ctk.CTkFrame(self.window)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # 对话历史
        self.chat_history = ctk.CTkTextbox(right_frame, wrap="word")
        self.chat_history.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        # 输入框和发送按钮
        input_frame = ctk.CTkFrame(right_frame)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        self.input_box = ctk.CTkTextbox(input_frame, height=60, wrap="word")
        self.input_box.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        send_button = ctk.CTkButton(input_frame, text="发送", command=self.send_message)
        send_button.pack(side="right")
        
        # 绑定回车键发送消息
        self.input_box.bind("<Return>", lambda e: self.send_message() if not e.state & 0x1 else None)
        
    def get_selected_philosophers(self):
        return [name for name, var in self.philosopher_vars.items() if var.get()]
        
    def send_message(self):
        user_message = self.input_box.get("1.0", "end-1c").strip()
        if not user_message:
            return
            
        selected_philosophers = self.get_selected_philosophers()
        if not selected_philosophers:
            self.chat_history.insert("end", "请至少选择一位哲学家进行对话\n\n")
            return
            
        self.chat_history.insert("end", f"你: {user_message}\n\n")
        self.input_box.delete("1.0", "end")
        
        # 创建新线程处理API请求
        threading.Thread(target=self.get_responses, args=(user_message, selected_philosophers)).start()
        
    def get_responses(self, user_message, selected_philosophers):
        for philosopher in selected_philosophers:
            try:
                # 添加当前用户消息到对话历史
                self.conversation_history[philosopher].append({'role': 'user', 'content': user_message})
                
                # 构建完整的消息历史，包括系统提示和所有对话历史
                system_prompt = self.philosophers[philosopher]
                messages = [{'role': 'system', 'content': system_prompt}]
                
                # 添加对话历史（包括之前的搜索结果）
                messages.extend(self.conversation_history[philosopher])
                
                response = self.client.chat.completions.create(
                    model=os.getenv('MODELSCOPE_MODEL'),
                    messages=messages,
                    stream=True
                )
                
                # 使用哲学家的显示名称
                display_name = self.philosopher_agents[philosopher].display_name
                self.chat_history.insert("end", f"{display_name}: ")
                
                # 收集完整响应以添加到对话历史
                full_response = ""
                
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        self.chat_history.insert("end", content)
                        self.chat_history.see("end")
                
                # 将AI响应添加到对话历史
                self.conversation_history[philosopher].append({'role': 'assistant', 'content': full_response})
                
                self.chat_history.insert("end", "\n\n")
                
            except Exception as e:
                self.chat_history.insert("end", f"Error getting response from {philosopher}: {str(e)}\n\n")
            
            self.chat_history.see("end")
        
    def perform_search(self):
        query = self.search_input.get().strip()
        if not query:
            self.chat_history.insert("end", "请输入搜索关键词\n\n")
            return
        
        self.chat_history.insert("end", f"正在搜索: {query}...\n")
        self.chat_history.see("end")
        
        # 执行搜索
        self.searcher.search(query, self.handle_search_results)
    
    def handle_search_results(self, results):
        if "error" in results:
            self.chat_history.insert("end", f"搜索错误: {results['error']}\n\n")
        else:
            search_info = results['results']
            self.chat_history.insert("end", f"搜索结果:\n{search_info}\n\n")
            
            # 将搜索结果添加到所有哲学家的对话历史中
            search_message = f"以下是关于 '{results['query']}' 的网络搜索结果，请在回答时参考这些信息:\n\n{search_info}"
            
            for philosopher in self.philosopher_agents.keys():
                self.conversation_history[philosopher].append({'role': 'user', 'content': search_message})
                self.conversation_history[philosopher].append({'role': 'assistant', 'content': "我已收到搜索结果，将在回答中参考这些信息。"})
        
        self.chat_history.see("end")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PhilosopherChat()
    app.run()
