#!/usr/bin/env python3
"""
ShizishanGPT Project Runner
Automated startup script for the complete ShizishanGPT agricultural AI system
"""

import subprocess
import time
import sys
import os
import signal
import requests
from pathlib import Path
import threading
import queue

# Configuration
BACKEND_PORT = 8000
MIDDLEWARE_PORT = 5000  
FRONTEND_PORT = 3000
OLLAMA_PORT = 11434
MONGODB_PORT = 27017

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ShizishanGPTRunner:
    def __init__(self):
        self.processes = {}
        self.project_root = Path(__file__).parent.absolute()
        
    def print_banner(self):
        """Print startup banner"""
        print(f"""
{Colors.CYAN}{'='*60}{Colors.END}
{Colors.BOLD}{Colors.GREEN}🌾 ShizishanGPT Agricultural AI System{Colors.END}
{Colors.CYAN}{'='*60}{Colors.END}

{Colors.YELLOW}🚀 Starting complete system stack...{Colors.END}

{Colors.BLUE}Components:{Colors.END}
  • Backend (FastAPI)     → Port {BACKEND_PORT}
  • Middleware (Node.js)  → Port {MIDDLEWARE_PORT} 
  • Frontend (React)      → Port {FRONTEND_PORT}
  • MongoDB Database      → Port {MONGODB_PORT}
  • Ollama (Gemma 2)      → Port {OLLAMA_PORT}

{Colors.CYAN}{'='*60}{Colors.END}
""")

    def check_service(self, name, url, timeout=5):
        """Check if a service is accessible"""
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code in [200, 404]:  # 404 is ok for some endpoints
                return True
        except:
            pass
        return False

    def kill_existing_processes(self):
        """Kill existing processes on required ports"""
        print(f"{Colors.YELLOW}🧹 Cleaning up existing processes...{Colors.END}")
        
        # Kill node processes (middleware/frontend)
        try:
            subprocess.run(["taskkill", "/f", "/im", "node.exe"], 
                         capture_output=True, check=False)
        except:
            pass
            
        # Kill python processes on backend port
        try:
            result = subprocess.run(
                f'netstat -ano | findstr :{BACKEND_PORT}',
                shell=True, capture_output=True, text=True
            )
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[4]
                        subprocess.run(f"taskkill /f /pid {pid}", 
                                     shell=True, capture_output=True)
        except:
            pass
            
        time.sleep(2)
        print(f"{Colors.GREEN}✅ Cleanup complete{Colors.END}")

    def check_dependencies(self):
        """Check if required dependencies are available"""
        print(f"{Colors.YELLOW}🔍 Checking dependencies...{Colors.END}")
        
        checks = []
        
        # Check MongoDB
        if self.check_service("MongoDB", f"http://localhost:{MONGODB_PORT}"):
            checks.append(("MongoDB", True))
        else:
            checks.append(("MongoDB", False))
            
        # Check Ollama
        if self.check_service("Ollama", f"http://localhost:{OLLAMA_PORT}"):
            checks.append(("Ollama", True))
        else:
            checks.append(("Ollama", False))
            
        # Check Python
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            checks.append(("Python", True))
        except:
            checks.append(("Python", False))
            
        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True)
            checks.append(("Node.js", True))
        except:
            checks.append(("Node.js", False))
            
        # Print results
        for name, status in checks:
            if status:
                print(f"  {Colors.GREEN}✅ {name}{Colors.END}")
            else:
                print(f"  {Colors.RED}❌ {name}{Colors.END}")
                
        failed = [name for name, status in checks if not status]
        if failed:
            print(f"\n{Colors.RED}❌ Missing dependencies: {', '.join(failed)}{Colors.END}")
            print(f"{Colors.YELLOW}Please install missing components and try again.{Colors.END}")
            return False
            
        print(f"{Colors.GREEN}✅ All dependencies available{Colors.END}")
        return True

    def start_backend(self):
        """Start FastAPI backend"""
        print(f"{Colors.BLUE}🚀 Starting Backend (FastAPI)...{Colors.END}")
        
        backend_cmd = [sys.executable, "-m", "src.backend.main"]
        
        process = subprocess.Popen(
            backend_cmd,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes['backend'] = process
        
        # Wait for startup
        for i in range(30):
            if self.check_service("Backend", f"http://localhost:{BACKEND_PORT}/health"):
                print(f"  {Colors.GREEN}✅ Backend running on port {BACKEND_PORT}{Colors.END}")
                return True
            time.sleep(1)
            
        print(f"  {Colors.RED}❌ Backend failed to start{Colors.END}")
        return False

    def start_middleware(self):
        """Start Node.js middleware"""
        print(f"{Colors.BLUE}🚀 Starting Middleware (Node.js)...{Colors.END}")
        
        middleware_dir = self.project_root / "middleware"
        
        process = subprocess.Popen(
            ["node", "server.js"],
            cwd=middleware_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.processes['middleware'] = process
        
        # Wait for startup
        for i in range(20):
            if self.check_service("Middleware", f"http://localhost:{MIDDLEWARE_PORT}/health"):
                print(f"  {Colors.GREEN}✅ Middleware running on port {MIDDLEWARE_PORT}{Colors.END}")
                return True
            time.sleep(1)
            
        print(f"  {Colors.RED}❌ Middleware failed to start{Colors.END}")
        return False

    def start_frontend(self):
        """Start React frontend"""
        print(f"{Colors.BLUE}🚀 Starting Frontend (React)...{Colors.END}")
        
        frontend_dir = self.project_root / "frontend"
        
        # Set environment to avoid browser opening
        env = os.environ.copy()
        env['BROWSER'] = 'none'
        
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        self.processes['frontend'] = process
        
        # Wait for startup (React takes longer)
        print(f"  {Colors.YELLOW}⏳ Waiting for React to compile...{Colors.END}")
        for i in range(60):
            if self.check_service("Frontend", f"http://localhost:{FRONTEND_PORT}"):
                print(f"  {Colors.GREEN}✅ Frontend running on port {FRONTEND_PORT}{Colors.END}")
                return True
            time.sleep(2)
            
        print(f"  {Colors.RED}❌ Frontend failed to start{Colors.END}")
        return False

    def run_system_test(self):
        """Run quick system integration test"""
        print(f"\n{Colors.YELLOW}🧪 Running system integration test...{Colors.END}")
        
        try:
            # Test frontend → middleware → backend → Gemma 2
            response = requests.post(
                f"http://localhost:{MIDDLEWARE_PORT}/ask",
                json={"query": "What is crop rotation?", "mode": "auto"},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', '')
                tools_used = result.get('tools_used', [])
                
                if answer and len(answer) > 50:
                    print(f"  {Colors.GREEN}✅ System integration test passed{Colors.END}")
                    print(f"  {Colors.CYAN}🔧 Tools used: {tools_used}{Colors.END}")
                    print(f"  {Colors.CYAN}📝 Response length: {len(answer)} characters{Colors.END}")
                    return True
                    
            print(f"  {Colors.RED}❌ System integration test failed{Colors.END}")
            return False
            
        except Exception as e:
            print(f"  {Colors.RED}❌ System test error: {e}{Colors.END}")
            return False

    def print_status(self):
        """Print system status and URLs"""
        print(f"""
{Colors.GREEN}{'='*60}{Colors.END}
{Colors.BOLD}{Colors.GREEN}🎉 ShizishanGPT System Started Successfully!{Colors.END}
{Colors.GREEN}{'='*60}{Colors.END}

{Colors.BOLD}🌐 Access URLs:{Colors.END}
  • Frontend:     {Colors.CYAN}http://localhost:{FRONTEND_PORT}{Colors.END}
  • Backend API:  {Colors.CYAN}http://localhost:{BACKEND_PORT}{Colors.END}
  • Middleware:   {Colors.CYAN}http://localhost:{MIDDLEWARE_PORT}{Colors.END}

{Colors.BOLD}🔧 System Features:{Colors.END}
  • {Colors.GREEN}✅ AgriChatbot with Gemma 2 LLM{Colors.END}
  • {Colors.GREEN}✅ 6-Tool Agent System (Yield, Pest, Weather, RAG, LLM, Translation){Colors.END}
  • {Colors.GREEN}✅ MongoDB Conversation Storage{Colors.END}
  • {Colors.GREEN}✅ React Frontend with Chat Interface{Colors.END}
  • {Colors.GREEN}✅ Complete Agricultural AI Pipeline{Colors.END}

{Colors.BOLD}🛠️ Available Modes:{Colors.END}
  • {Colors.YELLOW}LLM Mode:{Colors.END} Direct AI chat with Gemma 2
  • {Colors.YELLOW}RAG Mode:{Colors.END} Knowledge base retrieval
  • {Colors.YELLOW}Agent Mode:{Colors.END} Multi-tool agricultural assistant

{Colors.RED}Press Ctrl+C to stop all services{Colors.END}
{Colors.GREEN}{'='*60}{Colors.END}
""")

    def wait_for_shutdown(self):
        """Wait for shutdown signal"""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Gracefully shutdown all services"""
        print(f"\n{Colors.YELLOW}🛑 Shutting down ShizishanGPT system...{Colors.END}")
        
        for name, process in self.processes.items():
            try:
                print(f"  {Colors.YELLOW}Stopping {name}...{Colors.END}")
                process.terminate()
                process.wait(timeout=5)
                print(f"  {Colors.GREEN}✅ {name} stopped{Colors.END}")
            except subprocess.TimeoutExpired:
                print(f"  {Colors.RED}⚠️ Force killing {name}...{Colors.END}")
                process.kill()
            except Exception as e:
                print(f"  {Colors.RED}❌ Error stopping {name}: {e}{Colors.END}")
                
        print(f"{Colors.GREEN}✅ Shutdown complete{Colors.END}")

    def run(self):
        """Main run method"""
        try:
            self.print_banner()
            
            # Check dependencies
            if not self.check_dependencies():
                return False
                
            # Cleanup
            self.kill_existing_processes()
            
            # Start services in order
            if not self.start_backend():
                return False
                
            if not self.start_middleware():
                return False
                
            if not self.start_frontend():
                return False
                
            # Test system
            if not self.run_system_test():
                print(f"{Colors.YELLOW}⚠️ System test failed but services are running{Colors.END}")
                
            # Print status
            self.print_status()
            
            # Wait for shutdown
            self.wait_for_shutdown()
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error running system: {e}{Colors.END}")
            self.shutdown()
            return False

def main():
    """Main entry point"""
    runner = ShizishanGPTRunner()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        runner.shutdown()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    
    success = runner.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()