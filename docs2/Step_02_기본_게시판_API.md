# Step 2: 기본 게시판 API 개발

> **목표**: 데이터베이스를 연동하고 CRUD 기능을 가진 게시판 API를 만든다.

---

## 🎯 이 단계를 배우는 이유

### 왜 계층형 아키텍처인가?

프론트엔드에서도 **관심사의 분리**를 하듯이, 백엔드에서도 역할을 나눕니다.

```
프론트엔드                     백엔드
-------------------           -------------------
Component (UI)          ←→    Controller (HTTP)
Hook/Service (로직)     ←→    Service (비즈니스 로직)
API Call (데이터)       ←→    Repository (데이터베이스)
Type/Interface (모델)   ←→    Entity (데이터 구조)
```

### 실무에서 왜 이렇게 나누나?

1. **유지보수 용이**: 버그가 생기면 어느 계층인지 바로 알 수 있음
2. **테스트 용이**: 각 계층을 독립적으로 테스트 가능
3. **협업 용이**: 역할을 나눠서 동시에 개발 가능
4. **재사용 가능**: Service 로직은 다른 Controller에서도 사용 가능

---

## 💡 핵심 개념

### 1. 계층형 아키텍처 (Layered Architecture)

```
[클라이언트 (Postman/React)]
         ↓ HTTP 요청
[Controller Layer]  ← HTTP 요청/응답 처리
         ↓
[Service Layer]     ← 비즈니스 로직
         ↓
[Repository Layer]  ← 데이터베이스 접근
         ↓
[Database]          ← 데이터 저장
```

**각 계층의 역할**:

| 계층           | 역할                     | 하면 안 되는 것          |
| -------------- | ------------------------ | ------------------------ |
| **Controller** | HTTP 요청/응답, URL 매핑 | 비즈니스 로직, DB 접근   |
| **Service**    | 비즈니스 로직, 트랜잭션  | HTTP 처리, SQL 직접 작성 |
| **Repository** | 데이터베이스 CRUD        | 비즈니스 로직            |
| **Entity**     | 데이터 구조 정의         | 로직 포함 X              |

#### 프론트엔드 비유

```javascript
// Component (Controller)
function PostList() {
  const { posts, createPost } = usePostService(); // Service 사용

  return (
    <div>
      {posts.map((post) => (
        <PostItem post={post} />
      ))}
    </div>
  );
}

// Service (Service)
function usePostService() {
  const fetchPosts = async () => {
    const data = await postApi.getAll(); // Repository 사용
    // 비즈니스 로직 (필터링, 변환 등)
    return data;
  };
}

// API Call (Repository)
const postApi = {
  getAll: () => fetch("/api/posts").then((res) => res.json()),
};
```

---

### 2. JPA와 Entity

#### JPA (Java Persistence API)

- 자바에서 **ORM**(Object-Relational Mapping)을 사용하기 위한 표준
- **ORM**: 객체와 데이터베이스 테이블을 자동으로 매핑

#### 프론트엔드 비유: TypeScript Type vs Database Table

```typescript
// TypeScript Interface (프론트)
interface Post {
  id: number;
  title: string;
  content: string;
  createdAt: Date;
}
```

```java
// JPA Entity (백엔드)
@Entity  // 이 클래스는 데이터베이스 테이블과 매핑
public class Post {
    @Id
    @GeneratedValue
    private Long id;
    private String title;
    private String content;
    private LocalDateTime createdAt;
}
```

**JPA의 마법**:

- 위 Entity 클래스만 작성하면 자동으로 테이블 생성
- SQL을 직접 작성하지 않아도 CRUD 가능

---

### 3. Repository 패턴

#### 전통적인 방식 (SQL 직접 작성)

```java
public class PostRepository {
    public List<Post> findAll() {
        String sql = "SELECT * FROM post";
        // JDBC 코드 50줄...
    }

    public Post findById(Long id) {
        String sql = "SELECT * FROM post WHERE id = ?";
        // JDBC 코드 50줄...
    }
}
```

#### JPA Repository 방식

```java
public interface PostRepository extends JpaRepository<Post, Long> {
    // 메서드 작성 안 해도 자동 제공!
    // - findAll()
    // - findById()
    // - save()
    // - deleteById()
}
```

**프론트엔드 비유**: React Query, SWR

```javascript
// React Query - CRUD 함수를 자동으로 제공
const { data, refetch } = useQuery("posts", fetchPosts);
const { mutate } = useMutation(createPost);
```

---

### 4. 연관관계 매핑

게시판과 게시글의 관계:

- **하나의 게시판**은 **여러 개의 게시글**을 가짐 (1:N)

```java
// Board Entity
@Entity
public class Board {
    @Id
    @GeneratedValue
    private Long id;
    private String name;

    @OneToMany(mappedBy = "board")  // 1:N 관계
    private List<Post> posts = new ArrayList<>();
}

// Post Entity
@Entity
public class Post {
    @Id
    @GeneratedValue
    private Long id;
    private String title;
    private String content;

    @ManyToOne  // N:1 관계
    @JoinColumn(name = "board_id")
    private Board board;
}
```

**프론트엔드 비유**: 중첩된 데이터

```javascript
// Board
{
    id: 1,
    name: "공지사항",
    posts: [  // 1:N 관계
        { id: 1, title: "첫 글" },
        { id: 2, title: "두 번째 글" }
    ]
}

// Post
{
    id: 1,
    title: "첫 글",
    board: {  // N:1 관계
        id: 1,
        name: "공지사항"
    }
}
```

---

## 🛠️ 최소 구현 코드

### 1. Entity 생성

#### Post Entity

```java
// src/main/java/com/project/board/model/Post.java

package com.project.board.model;

import jakarta.persistence.*;
import lombok.Data;

@Entity  // JPA Entity임을 선언
@Data    // Lombok: Getter, Setter 자동 생성
public class Post {

    @Id  // 기본 키
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // 자동 증가
    private Long id;

    @Column(nullable = false, length = 200)  // NOT NULL, 최대 200자
    private String title;

    @Column(columnDefinition = "TEXT")  // 긴 텍스트
    private String content;

    @ManyToOne  // 게시글:게시판 = N:1
    @JoinColumn(name = "board_id")
    private Board board;
}
```

**어노테이션 설명**:

- `@Entity`: JPA가 관리하는 엔티티
- `@Id`: 기본 키 (Primary Key)
- `@GeneratedValue`: 자동 증가 (AUTO_INCREMENT)
- `@Column`: 컬럼 속성 지정
- `@ManyToOne`: 다대일 관계
- `@JoinColumn`: 외래 키 컬럼명 지정

#### Board Entity

```java
// src/main/java/com/project/board/model/Board.java

package com.project.board.model;

import jakarta.persistence.*;
import lombok.Data;
import com.fasterxml.jackson.annotation.JsonIgnore;
import java.util.ArrayList;
import java.util.List;

@Entity
@Data
public class Board {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String name;

    @OneToMany(mappedBy = "board")  // Post의 board 필드와 매핑
    @JsonIgnore  // JSON 변환 시 무한 순환 방지
    private List<Post> posts = new ArrayList<>();
}
```

---

### 2. Repository 생성

```java
// src/main/java/com/project/board/repository/PostRepository.java

package com.project.board.repository;

import com.project.board.model.Post;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PostRepository extends JpaRepository<Post, Long> {
    // JpaRepository<Entity타입, ID타입>

    // 기본 메서드 자동 제공:
    // - findAll(): 전체 조회
    // - findById(Long id): ID로 조회
    // - save(Post post): 저장/수정
    // - deleteById(Long id): 삭제
    // - count(): 개수

    // 커스텀 메서드 (필요 시 추가)
    // List<Post> findByBoardId(Long boardId);
}
```

```java
// src/main/java/com/project/board/repository/BoardRepository.java

package com.project.board.repository;

import com.project.board.model.Board;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface BoardRepository extends JpaRepository<Board, Long> {
}
```

**놀라운 점**:

- 인터페이스만 선언하면 끝!
- 구현 클래스는 스프링이 자동 생성
- SQL 작성 불필요

---

### 3. Service 생성

```java
// src/main/java/com/project/board/service/PostService.java

package com.project.board.service;

import com.project.board.model.Post;
import com.project.board.repository.PostRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service  // 서비스 빈 등록
@RequiredArgsConstructor  // final 필드 생성자 자동 생성
@Transactional(readOnly = true)  // 읽기 전용은 기본값
public class PostService {

    private final PostRepository postRepository;

    // 전체 조회
    public List<Post> findAll() {
        return postRepository.findAll();
    }

    // ID로 조회
    public Post findById(Long id) {
        return postRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("게시글을 찾을 수 없습니다. ID: " + id));
    }

    // 저장 (생성 & 수정)
    @Transactional  // 쓰기 작업은 트랜잭션 필요
    public Post save(Post post) {
        return postRepository.save(post);
    }

    // 수정
    @Transactional
    public Post update(Long id, Post post) {
        Post existingPost = findById(id);
        existingPost.setTitle(post.getTitle());
        existingPost.setContent(post.getContent());
        return postRepository.save(existingPost);
    }

    // 삭제
    @Transactional
    public void delete(Long id) {
        if (!postRepository.existsById(id)) {
            throw new RuntimeException("게시글을 찾을 수 없습니다. ID: " + id);
        }
        postRepository.deleteById(id);
    }
}
```

**`@RequiredArgsConstructor`의 마법**:

```java
// Lombok이 자동 생성하는 코드
public PostService(PostRepository postRepository) {
    this.postRepository = postRepository;
}
```

#### BoardService 생성

```java
// src/main/java/com/project/board/service/BoardService.java

package com.project.board.service;

import com.project.board.model.Board;
import com.project.board.repository.BoardRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)  // 읽기 전용은 기본값
public class BoardService {

    private final BoardRepository boardRepository;

    // 전체 조회
    public List<Board> findAll() {
        return boardRepository.findAll();
    }

    // ID로 조회
    public Board findById(Long id) {
        return boardRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("게시판을 찾을 수 없습니다. ID: " + id));
    }

    // 저장 (생성 & 수정)
    @Transactional  // 쓰기 작업은 트랜잭션 필요
    public Board save(Board board) {
        return boardRepository.save(board);
    }

    // 수정
    @Transactional
    public Board update(Long id, Board board) {
        Board existingBoard = findById(id);
        existingBoard.setName(board.getName());
        return boardRepository.save(existingBoard);
    }

    // 삭제
    @Transactional
    public void delete(Long id) {
        if (!boardRepository.existsById(id)) {
            throw new RuntimeException("게시판을 찾을 수 없습니다. ID: " + id);
        }
        boardRepository.deleteById(id);
    }
}
```

**트랜잭션 설명**:
- `@Transactional(readOnly = true)`: 클래스 레벨에서 읽기 전용 설정 (성능 최적화)
- `@Transactional`: 쓰기 작업(저장/수정/삭제)에만 트랜잭션 적용

---

### 4. Controller 생성

```java
// src/main/java/com/project/board/controller/PostController.java

package com.project.board.controller;

import com.project.board.model.Post;
import com.project.board.service.PostService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostController {

    private final PostService postService;

    // GET /api/posts - 전체 조회
    @GetMapping
    public ResponseEntity<List<Post>> list() {
        List<Post> posts = postService.findAll();
        return ResponseEntity.ok(posts);
    }

    // GET /api/posts/{id} - 상세 조회
    @GetMapping("/{id}")
    public ResponseEntity<Post> get(@PathVariable Long id) {
        Post post = postService.findById(id);
        return ResponseEntity.ok(post);
    }

    // POST /api/posts - 생성
    @PostMapping
    public ResponseEntity<Post> create(@RequestBody Post post) {
        Post savedPost = postService.save(post);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedPost);
    }

    // PUT /api/posts/{id} - 수정
    @PutMapping("/{id}")
    public ResponseEntity<Post> update(
            @PathVariable Long id,
            @RequestBody Post post) {
        Post updatedPost = postService.update(id, post);
        return ResponseEntity.ok(updatedPost);
    }

    // DELETE /api/posts/{id} - 삭제
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        postService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

**어노테이션 설명**:

- `@PathVariable`: URL 경로의 변수 추출 (예: `/posts/1`의 `1`)
- `@RequestBody`: HTTP Body의 JSON을 객체로 변환
- `ResponseEntity`: HTTP 상태 코드와 함께 응답

**프론트엔드 비유**:

```javascript
// Express.js
app.get("/api/posts", (req, res) => {
  res.json(posts);
});

app.post("/api/posts", (req, res) => {
  const post = req.body;
  res.status(201).json(post);
});
```

#### BoardController 생성

```java
// src/main/java/com/project/board/controller/BoardController.java

package com.project.board.controller;

import com.project.board.model.Board;
import com.project.board.service.BoardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/boards")
@RequiredArgsConstructor
public class BoardController {

    private final BoardService boardService;

    // GET /api/boards - 전체 조회
    @GetMapping
    public ResponseEntity<List<Board>> list() {
        List<Board> boards = boardService.findAll();
        return ResponseEntity.ok(boards);
    }

    // GET /api/boards/{id} - 상세 조회
    @GetMapping("/{id}")
    public ResponseEntity<Board> get(@PathVariable Long id) {
        Board board = boardService.findById(id);
        return ResponseEntity.ok(board);
    }

    // POST /api/boards - 생성
    @PostMapping
    public ResponseEntity<Board> create(@RequestBody Board board) {
        Board savedBoard = boardService.save(board);
        return ResponseEntity.status(HttpStatus.CREATED).body(savedBoard);
    }

    // PUT /api/boards/{id} - 수정
    @PutMapping("/{id}")
    public ResponseEntity<Board> update(
            @PathVariable Long id,
            @RequestBody Board board) {
        Board updatedBoard = boardService.update(id, board);
        return ResponseEntity.ok(updatedBoard);
    }

    // DELETE /api/boards/{id} - 삭제
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        boardService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

---

### 5. application.properties 설정

```properties
# src/main/resources/application.properties

# 서버 포트
server.port=8080

# H2 Database
spring.h2.console.enabled=true
spring.datasource.url=jdbc:h2:mem:boarddb
spring.datasource.driverClassName=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=

# JPA 설정
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.jpa.hibernate.ddl-auto=create
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# Logging
logging.level.org.hibernate.SQL=DEBUG
logging.level.org.hibernate.type.descriptor.sql.BasicBinder=TRACE
```

**설정 설명**:

- `spring.h2.console.enabled=true`: H2 웹 콘솔 활성화
- `spring.jpa.hibernate.ddl-auto=create`: 테이블 자동 생성
- `spring.jpa.show-sql=true`: 실행되는 SQL 로그 출력

---

## 📝 실습 가이드

### Step 1: Entity 생성

1. `model` 패키지 생성
2. `Board.java`, `Post.java` 생성
3. 위 코드 작성

### Step 2: Repository 생성

1. `repository` 패키지 생성
2. `BoardRepository.java`, `PostRepository.java` 생성
3. `JpaRepository` 상속

### Step 3: Service 생성

1. `service` 패키지 생성
2. `PostService.java`, `BoardService.java` 생성
3. CRUD 메서드 작성
4. `@Transactional` 어노테이션 추가

### Step 4: Controller 생성

1. `controller` 패키지 생성
2. `PostController.java`, `BoardController.java` 생성
3. REST API 엔드포인트 작성

### Step 5: 애플리케이션 실행

1. `BoardApplication.java` 실행
2. 콘솔에서 SQL 로그 확인
3. H2 콘솔 접속: http://localhost:8080/h2-console
   - JDBC URL: `jdbc:h2:mem:boarddb`
   - Username: `sa`
   - Password: (빈칸)

### Step 6: Postman으로 테스트

#### 1. 게시판 생성

```
POST http://localhost:8080/api/boards
Content-Type: application/json

{
    "name": "공지사항"
}
```

#### 2. 게시글 생성

```
POST http://localhost:8080/api/posts
Content-Type: application/json

{
    "title": "첫 번째 게시글",
    "content": "안녕하세요!",
    "board": {
        "id": 1
    }
}
```

#### 3. 전체 조회

```
GET http://localhost:8080/api/posts
```

#### 4. 상세 조회

```
GET http://localhost:8080/api/posts/1
```

#### 5. 수정

```
PUT http://localhost:8080/api/posts/1
Content-Type: application/json

{
    "title": "수정된 제목",
    "content": "수정된 내용"
}
```

#### 6. 삭제

```
DELETE http://localhost:8080/api/posts/1
```

---

## 🎓 다음 단계로

### 이 단계에서 배운 것

- ✅ Entity-Repository-Service-Controller 패턴
- ✅ JPA를 활용한 데이터베이스 연동
- ✅ CRUD API 구현
- ✅ 1:N 연관관계 매핑
- ✅ Postman으로 API 테스트

### 아직 부족한 것

- ❌ 예외 처리 (게시글 없을 때)
- ❌ 입력 검증 (빈 제목 등)
- ❌ 페이징, 검색 기능
- ❌ 댓글 기능

### 다음 단계 예고: Step 3 - 게시판 기능 확장

**Step 3에서 배울 것**:

1. **댓글 기능**: Reply Entity 추가, 1:N 관계
2. **페이징**: Page, Pageable 사용
3. **검색**: 제목/내용 검색
4. **DTO 패턴**: Entity를 직접 반환하지 않기
5. **예외 처리**: @ControllerAdvice

---

## 💡 핵심 정리

### 개발 흐름

```
1. Entity 설계     → 데이터 구조 정의
2. Repository 생성 → 데이터 접근
3. Service 작성    → 비즈니스 로직
4. Controller 작성 → API 엔드포인트
5. 테스트          → Postman
```

### 각 계층의 역할 (다시 한번)

```
Controller: "POST /api/posts 요청이 왔네? Service에게 전달!"
Service:    "게시글 저장? Repository에게 부탁!"
Repository: "save() 호출? SQL 생성해서 DB에 저장!"
Database:   "데이터 저장 완료!"
```

### JPA의 장점

- SQL 작성 불필요
- 데이터베이스 변경 쉬움 (H2 → MySQL)
- 객체 지향적 코드

---

**준비되셨나요? Step 3으로 넘어가서 댓글, 페이징, 검색 기능을 추가해봅시다! 🚀**

```bash
# 다음 문서
dont_upload/Step_03_게시판_기능_확장.md
```
