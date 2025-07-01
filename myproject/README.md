# How to rebuild /mnt/myproject

cd /mnt
python3 -m venv myproject
cd myproject
source bin/activate
pip install -r requirements-myproject-frozen.txt

copy this to ~/.bashrc
# ~/.bashrc
if [[ $- == *i* ]]; then
    #cd_highest_course
    cd /mnt/myproject
    source bin/activate
    cd /mnt/AI-Agents-in-LangGraph
   #cd /mnt/coursera/course11
fi

