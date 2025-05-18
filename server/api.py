from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import Agent, Task, Result
from .storage import get_session
from .utils import generate_id, log_info

router = APIRouter()

@router.post("/agents/", response_model=dict)
def register_agent(name: str, ip: str = None, db: Session = Depends(get_session)):
    agent_id = generate_id()
    agent = Agent(id=agent_id, name=name, ip=ip)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    log_info(f"Agent registered: {agent_id} ({name})")
    return {"id": agent_id, "name": name, "ip": ip}

@router.get("/agents/", response_model=list)
def list_agents(db: Session = Depends(get_session)):
    agents = db.query(Agent).all()
    return [{"id": a.id, "name": a.name, "ip": a.ip, "status": a.status} for a in agents]

@router.post("/tasks/", response_model=dict)
def create_task(agent_id: str, command: str, db: Session = Depends(get_session)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    task_id = generate_id()
    task = Task(id=task_id, agent_id=agent_id, command=command)
    db.add(task)
    db.commit()
    db.refresh(task)
    log_info(f"Task created: {task_id} for agent {agent_id}")
    return {"id": task_id, "agent_id": agent_id, "command": command, "status": task.status}

@router.get("/tasks/{agent_id}", response_model=list)
def get_tasks(agent_id: str, db: Session = Depends(get_session)):
    tasks = db.query(Task).filter(Task.agent_id == agent_id).all()
    return [{"id": t.id, "command": t.command, "status": t.status} for t in tasks]

@router.post("/results/", response_model=dict)
def submit_result(task_id: str, output: str, db: Session = Depends(get_session)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    result_id = generate_id()
    result = Result(id=result_id, task_id=task_id, output=output)
    task.status = "done"
    db.add(result)
    db.commit()
    log_info(f"Result submitted for task {task_id}")
    return {"id": result_id, "task_id": task_id, "output": output}
