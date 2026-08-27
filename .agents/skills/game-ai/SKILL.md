---
name: game-ai
description: Game AI development guide covering behavior trees, state machines, pathfinding, and decision-making systems. Use when implementing enemy AI, NPC behaviors, flocking, tactical AI, or any intelligent agent behaviors in games. Includes Godot-specific implementations.
---

# 游戏 AI 开发指南

## AI 架构选择

### 架构对比
```yaml
有限状态机 (FSM):
  优点: 简单、直观、易于调试
  缺点: 状态多时难以维护
  适用: 简单敌人、Boss 阶段
  
行为树 (BT):
  优点: 模块化、可复用、易扩展
  缺点: 需要框架支持
  适用: 复杂 NPC、战术 AI
  
效用系统 (Utility AI):
  优点: 灵活、智能决策
  缺点: 参数调节困难
  适用: 模拟人生类、策略游戏
  
GOAP:
  优点: 目标导向、动态规划
  缺点: 计算成本高
  适用: 智能敌人、复杂行为
```

## 有限状态机 (FSM)

### 基础实现
```csharp
public enum EnemyState
{
    Idle,
    Patrol,
    Chase,
    Attack,
    Flee
}

public class EnemyFSM : Node
{
    private EnemyState _currentState;
    private Dictionary<EnemyState, IState> _states;
    
    public override void _Ready()
    {
        _states = new Dictionary<EnemyState, IState>
        {
            [EnemyState.Idle] = new IdleState(this),
            [EnemyState.Patrol] = new PatrolState(this),
            [EnemyState.Chase] = new ChaseState(this),
            [EnemyState.Attack] = new AttackState(this),
            [EnemyState.Flee] = new FleeState(this)
        };
        
        ChangeState(EnemyState.Idle);
    }
    
    public void ChangeState(EnemyState newState)
    {
        _states[_currentState]?.Exit();
        _currentState = newState;
        _states[_currentState]?.Enter();
    }
    
    public override void _Process(double delta)
    {
        _states[_currentState]?.Update(delta);
    }
}

public interface IState
{
    void Enter();
    void Update(double delta);
    void Exit();
}

public class ChaseState : IState
{
    private readonly EnemyFSM _fsm;
    private readonly CharacterBody2D _owner;
    private NavigationAgent2D _navAgent;
    
    public ChaseState(EnemyFSM fsm)
    {
        _fsm = fsm;
        _owner = fsm.GetParent<CharacterBody2D>();
        _navAgent = _owner.GetNode<NavigationAgent2D>("NavigationAgent2D");
    }
    
    public void Enter()
    {
        // 开始追逐动画
        _owner.GetNode<AnimationPlayer>("AnimationPlayer").Play("run");
    }
    
    public void Update(double delta)
    {
        var player = GetTree().GetFirstNodeInGroup("player") as Node2D;
        if (player == null) return;
        
        // 更新目标位置
        _navAgent.TargetPosition = player.GlobalPosition;
        
        // 移动向玩家
        var direction = _owner.ToLocal(_navAgent.GetNextPathPosition()).Normalized();
        _owner.Velocity = direction * _owner.Speed;
        _owner.MoveAndSlide();
        
        // 检查距离
        float distance = _owner.GlobalPosition.DistanceTo(player.GlobalPosition);
        if (distance < 50)
        {
            _fsm.ChangeState(EnemyState.Attack);
        }
        else if (distance > 500)
        {
            _fsm.ChangeState(EnemyState.Patrol);
        }
    }
    
    public void Exit()
    {
        _owner.Velocity = Vector2.Zero;
    }
}
```

## 行为树 (Behavior Tree)

### 节点类型
```yaml
复合节点:
  Sequence: 顺序执行（一个失败则失败）
  Selector: 选择执行（一个成功则成功）
  Parallel: 并行执行
  
装饰节点:
  Inverter: 反转结果
  Repeater: 重复执行
  UntilFail: 直到失败
  
叶子节点:
  Condition: 条件检查
  Action: 执行动作
```

### 行为树实现
```csharp
public enum NodeStatus
{
    Running,
    Success,
    Failure
}

public abstract class BTNode
{
    public abstract NodeStatus Execute();
}

public class Sequence : BTNode
{
    private readonly List<BTNode> _children = new();
    private int _currentChild = 0;
    
    public Sequence(params BTNode[] children)
    {
        _children.AddRange(children);
    }
    
    public override NodeStatus Execute()
    {
        while (_currentChild < _children.Count)
        {
            var status = _children[_currentChild].Execute();
            
            if (status == NodeStatus.Running)
                return NodeStatus.Running;
            
            if (status == NodeStatus.Failure)
            {
                _currentChild = 0;
                return NodeStatus.Failure;
            }
            
            _currentChild++;
        }
        
        _currentChild = 0;
        return NodeStatus.Success;
    }
}

public class Selector : BTNode
{
    private readonly List<BTNode> _children = new();
    private int _currentChild = 0;
    
    public Selector(params BTNode[] children)
    {
        _children.AddRange(children);
    }
    
    public override NodeStatus Execute()
    {
        while (_currentChild < _children.Count)
        {
            var status = _children[_currentChild].Execute();
            
            if (status == NodeStatus.Running)
                return NodeStatus.Running;
            
            if (status == NodeStatus.Success)
            {
                _currentChild = 0;
                return NodeStatus.Success;
            }
            
            _currentChild++;
        }
        
        _currentChild = 0;
        return NodeStatus.Failure;
    }
}

// 使用示例
public class EnemyAI : Node
{
    private BTNode _behaviorTree;
    
    public override void _Ready()
    {
        _behaviorTree = new Selector(
            // 优先攻击
            new Sequence(
                new Condition(IsPlayerInRange),
                new Condition(HasAmmo),
                new Action(Attack)
            ),
            // 追逐玩家
            new Sequence(
                new Condition(CanSeePlayer),
                new Action(ChasePlayer)
            ),
            // 巡逻
            new Action(Patrol)
        );
    }
    
    public override void _Process(double delta)
    {
        _behaviorTree.Execute();
    }
}
```

## 寻路算法

### A* 算法
```csharp
public class AStar
{
    private readonly Grid _grid;
    
    public List<Point> FindPath(Point start, Point end)
    {
        var openSet = new PriorityQueue<Point>();
        var cameFrom = new Dictionary<Point, Point>();
        var gScore = new Dictionary<Point, float>();
        var fScore = new Dictionary<Point, float>();
        
        openSet.Enqueue(start, 0);
        gScore[start] = 0;
        fScore[start] = Heuristic(start, end);
        
        while (openSet.Count > 0)
        {
            var current = openSet.Dequeue();
            
            if (current == end)
                return ReconstructPath(cameFrom, current);
            
            foreach (var neighbor in _grid.GetNeighbors(current))
            {
                float tentativeGScore = gScore[current] + _grid.GetCost(current, neighbor);
                
                if (!gScore.ContainsKey(neighbor) || tentativeGScore < gScore[neighbor])
                {
                    cameFrom[neighbor] = current;
                    gScore[neighbor] = tentativeGScore;
                    fScore[neighbor] = gScore[neighbor] + Heuristic(neighbor, end);
                    
                    if (!openSet.Contains(neighbor))
                        openSet.Enqueue(neighbor, fScore[neighbor]);
                }
            }
        }
        
        return null; // 无路径
    }
    
    private float Heuristic(Point a, Point b)
    {
        // 曼哈顿距离
        return Math.Abs(a.X - b.X) + Math.Abs(a.Y - b.Y);
    }
    
    private List<Point> ReconstructPath(Dictionary<Point, Point> cameFrom, Point current)
    {
        var path = new List<Point> { current };
        
        while (cameFrom.ContainsKey(current))
        {
            current = cameFrom[current];
            path.Insert(0, current);
        }
        
        return path;
    }
}
```

### Godot NavigationAgent2D
```csharp
public class EnemyNavigation : CharacterBody2D
{
    private NavigationAgent2D _navAgent;
    private Node2D _target;
    
    public override void _Ready()
    {
        _navAgent = GetNode<NavigationAgent2D>("NavigationAgent2D");
        
        // 配置
        _navAgent.PathDesiredDistance = 10.0f;
        _navAgent.TargetDesiredDistance = 10.0f;
        _navAgent.Radius = 20.0f;
        
        // 连接信号
        _navAgent.VelocityComputed += OnVelocityComputed;
    }
    
    public void SetTarget(Node2D target)
    {
        _target = target;
        UpdatePath();
    }
    
    private async void UpdatePath()
    {
        if (_target == null) return;
        
        // 异步计算路径
        _navAgent.TargetPosition = _target.GlobalPosition;
        await ToSignal(_navAgent, NavigationAgent2D.SignalName.PathChanged);
    }
    
    public override void _PhysicsProcess(double delta)
    {
        if (_navAgent.IsNavigationFinished())
            return;
        
        var nextPos = _navAgent.GetNextPathPosition();
        var direction = GlobalPosition.DirectionTo(nextPos);
        var velocity = direction * Speed;
        
        // 避障
        _navAgent.Velocity = velocity;
    }
    
    private void OnVelocityComputed(Vector2 safeVelocity)
    {
        Velocity = safeVelocity;
        MoveAndSlide();
    }
}
```

## 群体行为

### Boids 算法
```csharp
public class Boid : Node2D
{
    private Vector2 _velocity;
    private List<Boid> _neighbors = new();
    
    public override void _Process(double delta)
    {
        // 更新邻居列表
        UpdateNeighbors();
        
        // 计算三个力
        var separation = CalculateSeparation();
        var alignment = CalculateAlignment();
        var cohesion = CalculateCohesion();
        
        // 合并力
        var acceleration = separation * 1.5f + alignment * 1.0f + cohesion * 1.0f;
        
        // 更新速度和位置
        _velocity += acceleration * (float)delta;
        _velocity = _velocity.LimitLength(MaxSpeed);
        
        Position += _velocity * (float)delta;
    }
    
    private Vector2 CalculateSeparation()
    {
        var steer = Vector2.Zero;
        int count = 0;
        
        foreach (var neighbor in _neighbors)
        {
            float distance = Position.DistanceTo(neighbor.Position);
            if (distance > 0 && distance < SeparationRadius)
            {
                var diff = Position - neighbor.Position;
                diff = diff.Normalized() / distance;
                steer += diff;
                count++;
            }
        }
        
        if (count > 0)
            steer /= count;
        
        return steer;
    }
    
    private Vector2 CalculateAlignment()
    {
        var avgVelocity = Vector2.Zero;
        int count = 0;
        
        foreach (var neighbor in _neighbors)
        {
            if (Position.DistanceTo(neighbor.Position) < AlignmentRadius)
            {
                avgVelocity += neighbor._velocity;
                count++;
            }
        }
        
        if (count > 0)
        {
            avgVelocity /= count;
            avgVelocity = avgVelocity.Normalized() * MaxSpeed;
            return avgVelocity - _velocity;
        }
        
        return Vector2.Zero;
    }
    
    private Vector2 CalculateCohesion()
    {
        var center = Vector2.Zero;
        int count = 0;
        
        foreach (var neighbor in _neighbors)
        {
            if (Position.DistanceTo(neighbor.Position) < CohesionRadius)
            {
                center += neighbor.Position;
                count++;
            }
        }
        
        if (count > 0)
        {
            center /= count;
            return (center - Position).Normalized() * MaxSpeed - _velocity;
        }
        
        return Vector2.Zero;
    }
}
```

## 决策系统

### 效用 AI
```csharp
public class UtilityAI
{
    private readonly List<UtilityAction> _actions = new();
    
    public void AddAction(UtilityAction action)
    {
        _actions.Add(action);
    }
    
    public UtilityAction ChooseBestAction()
    {
        float bestScore = float.MinValue;
        UtilityAction bestAction = null;
        
        foreach (var action in _actions)
        {
            float score = action.CalculateScore();
            
            // 添加随机性
            score += GD.Randf() * 0.1f;
            
            if (score > bestScore)
            {
                bestScore = score;
                bestAction = action;
            }
        }
        
        return bestAction;
    }
}

public abstract class UtilityAction
{
    public abstract float CalculateScore();
    public abstract void Execute();
}

public class AttackAction : UtilityAction
{
    private readonly Enemy _enemy;
    
    public AttackAction(Enemy enemy)
    {
        _enemy = enemy;
    }
    
    public override float CalculateScore()
    {
        float score = 0f;
        
        // 玩家距离近，分数高
        float distance = _enemy.DistanceToPlayer();
        score += Mathf.Clamp(1.0f - distance / 200.0f, 0, 1) * 0.5f;
        
        // 有弹药，分数高
        score += _enemy.HasAmmo ? 0.3f : 0.0f;
        
        // 生命值高，更倾向于攻击
        score += _enemy.HealthPercent * 0.2f;
        
        return score;
    }
    
    public override void Execute()
    {
        _enemy.Attack();
    }
}
```

## 感知系统

### 视觉感知
```csharp
public class VisionSensor : Node2D
{
    [Export] public float ViewDistance = 300.0f;
    [Export] public float ViewAngle = 90.0f;
    [Export] public LayerMask VisionLayer;
    
    public Node2D Target { get; private set; }
    
    public override void _Process(double delta)
    {
        Target = null;
        
        var players = GetTree().GetNodesInGroup("player");
        foreach (Node2D player in players)
        {
            if (CanSee(player))
            {
                Target = player;
                break;
            }
        }
    }
    
    private bool CanSee(Node2D target)
    {
        var direction = target.GlobalPosition - GlobalPosition;
        float distance = direction.Length();
        
        // 检查距离
        if (distance > ViewDistance)
            return false;
        
        // 检查角度
        float angle = Mathf.RadToDeg(direction.Angle());
        float angleDiff = Mathf.Abs(Mathf.AngleDifference(angle, GlobalRotationDegrees));
        if (angleDiff > ViewAngle / 2)
            return false;
        
        // 射线检测
        var space = GetWorld2D().DirectSpaceState;
        var query = new PhysicsRayQueryParameters2D
        {
            From = GlobalPosition,
            To = target.GlobalPosition,
            CollisionMask = VisionLayer
        };
        
        var result = space.IntersectRay(query);
        if (result.Count > 0)
        {
            var collider = result["collider"].As<Node>();
            return collider == target;
        }
        
        return true;
    }
    
    // 可视化调试
    public override void _Draw()
    {
        // 绘制视野扇形
        DrawArc(Vector2.Zero, ViewDistance, -ViewAngle / 2, ViewAngle / 2, 32, Colors.Yellow, 1.0f);
    }
}
```

## 参考资源

- **行为树模式**: [references/behavior-trees.md](references/behavior-trees.md)
- **寻路算法**: [references/pathfinding.md](references/pathfinding.md)
- **高级技术**: [references/advanced-ai.md](references/advanced-ai.md)
