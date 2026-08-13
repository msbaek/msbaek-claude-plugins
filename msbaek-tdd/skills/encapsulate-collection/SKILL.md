---
name: encapsulate-collection
description: 컬렉션 getter가 내부 상태를 직접 노출하는 것을 방지하고 unmodifiable 반환 + add/remove 메서드 제공. /encapsulate-collection으로 호출.
argument-hint: "[commit-ref]"
---

# Encapsulate Collection

## GOAL

컬렉션을 반환하는 getter가 내부 상태를 직접 노출하는 것을 방지하여:
- 불변성(Immutability) 보장
- 캡슐화 원칙 준수
- 의도하지 않은 외부 수정 방지
- First Class Collection의 첫 단계

## CONSTRAINTS

- **동작 변경 금지**: 구조 개선만 수행 (기능 변경 없음)
- **테스트 수정 금지**: 구조 변경이 테스트를 깨면 되돌리기
- **사용자 확인 필수**: 자동 적용 금지
- **명시적 git add**: `git add -A` 금지, 변경된 파일만 명시
- **단일 커밋**: 하나의 `refactor:` 커밋으로 완료

## 적용 패턴

### Before: 내부 컬렉션 직접 노출
```java
class Course {
    private List<Student> students = new ArrayList<>();
    
    public List<Student> getStudents() {
        return students;  // 위험: 외부에서 수정 가능
    }
}

// 호출부: 캡슐화 위반
course.getStudents().add(student);  // 직접 수정
course.getStudents().clear();       // 위험한 조작
```

### After: Unmodifiable 반환 + 명시적 메서드
```java
class Course {
    private List<Student> students = new ArrayList<>();
    
    public List<Student> getStudents() {
        return Collections.unmodifiableList(students);
    }
    
    public void addStudent(Student student) {
        students.add(student);
    }
    
    public void removeStudent(Student student) {
        students.remove(student);
    }
}

// 호출부: 명시적 메서드 사용
course.addStudent(student);
course.removeStudent(student);
```

### 추가 예시: Set 컬렉션
```java
class Team {
    private Set<Member> members = new HashSet<>();
    
    public Set<Member> getMembers() {
        return Collections.unmodifiableSet(members);
    }
    
    public void addMember(Member member) {
        members.add(member);
    }
    
    public void removeMember(Member member) {
        members.remove(member);
    }
    
    public boolean hasMember(Member member) {
        return members.contains(member);
    }
}
```

### 추가 예시: 복사본 반환 (방어적 복사)
```java
class Order {
    private List<OrderItem> items = new ArrayList<>();
    
    // Option 1: Unmodifiable (읽기 전용)
    public List<OrderItem> getItems() {
        return Collections.unmodifiableList(items);
    }
    
    // Option 2: 방어적 복사 (완전 격리)
    public List<OrderItem> getItemsCopy() {
        return new ArrayList<>(items);
    }
}
```

### 반대 방향도 같다 — 생성자로 받은 컬렉션을 그대로 보관하지 않는다

getter는 컬렉션이 **나가는** 지점이고 생성자는 **들어오는** 지점이다. 나가는 쪽만
막으면 캡슐화는 절반이다 — 호출자가 넘긴 리스트를 참조로 보관하면, 그 리스트는
객체 밖에 여전히 살아 있어 호출자가 나중에 바꿀 수 있고, 반대로 그 리스트의 성질
(불변인지 가변인지)이 객체 안으로 그대로 새어 들어온다.

```java
class Cart {
    private List<CartLine> lines;

    public Cart(List<CartLine> lines) {
        this.lines = lines;                    // ❌ 참조를 그대로 보관
    }
}

class Cart {
    private final List<CartLine> lines;

    public Cart(List<CartLine> lines) {
        this.lines = new ArrayList<>(lines);   // ✅ 들어올 때 복사
    }
}
```

**JPA 엔티티에서 실제로 터지는 형태**: `List.of(...)`로 만든 리스트를 그대로 보관한
엔티티를 재저장하면 Hibernate가 병합 과정에서 그 컬렉션에 `clear()`를 호출해
`UnsupportedOperationException`이 난다. 이때 손볼 곳은 Hibernate 설정이 아니라
생성자다 — 불변 리스트가 필드로 들어간 것이 원인이고, 생성자 복사가 그 경로를 끊는다.

`private final`로 두면 컴파일러가 재할당을 막아 주지만 **컬렉션 내용의 변경은 막지
못한다** — final은 참조를 고정할 뿐이다. 들어올 때 복사(생성자) + 나갈 때 보호
(getter, 위 예시) 두 지점을 모두 막아야 캡슐화가 닫힌다.

## First Class Collection으로 발전

이 기법 적용 후 `/first-class-collection` 스킬로 전용 클래스 추출 가능:

```java
// Encapsulate Collection 적용 후
class Course {
    private Students students = new Students();  // First Class Collection
    
    public Students getStudents() { return students; }
}

class Students {
    private List<Student> students = new ArrayList<>();
    
    public void add(Student student) { students.add(student); }
    public void remove(Student student) { students.remove(student); }
    public int size() { return students.size(); }
    public boolean contains(Student student) { return students.contains(student); }
}
```

## 적용 기준

### ✅ 적용 대상
- `public List<T> getXxx()` 패턴
- 내부 컬렉션을 그대로 반환하는 getter
- 외부에서 `getXxx().add()` 호출하는 코드
- 도메인 객체의 컬렉션 필드
- **생성자·팩토리가 받은 컬렉션을 그대로 필드에 보관하는 코드** (위 "반대 방향" 참조)

### ❌ 적용 제외
- **DTO/VO**: 단순 데이터 전송 객체 (불변성 불필요)
- **Builder 패턴**: 빌더 내부 컬렉션 (완성 전까지 가변)
- **읽기 전용 래퍼**: 이미 Unmodifiable 반환 중
- **불변 컬렉션**: `List.of()`, `Set.of()` 사용 중

### ⚠️ 주의사항
- 호출부에서 `getXxx().add()` 패턴 모두 변경 필요
- 테스트 코드도 영향받음 (명시적 메서드 사용으로 전환)
- Unmodifiable vs 방어적 복사 선택:
  - **읽기 전용**: `Collections.unmodifiableList()` (성능 우수)
  - **완전 격리**: `new ArrayList<>(...)` (안전성 우수)

## OUTPUT FORMAT

### 실행 절차

1. **대상 파일 수집**
   ```bash
   # commit-ref 제공 시
   git diff <commit-ref> --name-only '*.java'
   
   # 미제공 시 현재 변경사항
   git diff --name-only '*.java'
   ```

2. **후보 식별 및 제시**
   - 컬렉션 타입 getter 탐지 (`List<T>`, `Set<T>`, `Map<K,V>`)
   - 내부 필드를 직접 반환하는지 확인
   - 호출부에서 `getXxx().add()` 패턴 검색
   - 각 후보에 대해:
     - 파일명 및 라인 번호
     - Before/After 코드 미리보기
     - 영향받는 호출부 수

3. **사용자 확인**
   ```
   발견된 후보 2개:
   
   1. Course.java:15
      getter: public List<Student> getStudents()
      → Collections.unmodifiableList() 반환
      → addStudent(), removeStudent() 메서드 추가
      영향받는 호출부: 5곳 (course.getStudents().add() 패턴)
   
   2. Team.java:20
      getter: public Set<Member> getMembers()
      → Collections.unmodifiableSet() 반환
      → addMember(), removeMember() 메서드 추가
      영향받는 호출부: 3곳
   
   적용하시겠습니까? (yes / no / 수정)
   Unmodifiable vs 방어적 복사 선택: (unmodifiable / copy)
   ```

4. **리팩토링 적용**
   - getter를 Unmodifiable 또는 방어적 복사로 변경
   - `add()`, `remove()` 메서드 추가
   - 모든 호출부 업데이트:
     - `getXxx().add(item)` → `addXxx(item)`
     - `getXxx().remove(item)` → `removeXxx(item)`
   - (선택) 추가 메서드 (`contains()`, `size()`, `isEmpty()`)

5. **테스트 실행**
   ```bash
   ./gradlew test  # 또는 mvn test
   ```

6. **커밋 또는 되돌리기**
   ```bash
   # 테스트 통과 시
   git add <변경된파일.java>
   git commit -m "refactor: encapsulate collection in <클래스명>"
   
   # 테스트 실패 시
   git checkout -- <변경된파일.java>
   ```

### 출력 예시
```
✅ Encapsulate Collection 완료

변경 내용:
- Course.java:15
  getStudents() → Collections.unmodifiableList() 반환
  + addStudent(Student)
  + removeStudent(Student)
  
- Team.java:20
  getMembers() → Collections.unmodifiableSet() 반환
  + addMember(Member)
  + removeMember(Member)

영향받는 호출부: 8곳 자동 업데이트

테스트: ✅ 모든 테스트 통과 (23 tests)
커밋: refactor: encapsulate collection in Course, Team

💡 제안: Course.students는 First Class Collection으로 추출 가능합니다.
   /first-class-collection 스킬을 고려해보세요.
```

## FAILURE CONDITIONS

이 조건 중 하나라도 발생 시 작업 실패로 간주:

- [ ] 테스트가 실패함 (리팩토링 후)
- [ ] DTO/VO 클래스에 불필요하게 적용함
- [ ] 호출부 업데이트 누락 (`getXxx().add()` 패턴이 남음)
- [ ] 사용자 확인 없이 자동 적용함
- [ ] 여러 개의 커밋으로 분리됨
- [ ] `git add -A` 사용함
- [ ] Unmodifiable 반환 후에도 외부에서 수정 가능한 상태
