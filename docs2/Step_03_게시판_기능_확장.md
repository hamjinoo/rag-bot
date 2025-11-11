# Step 3: 게시판 기능 확장

> **목표**: 댓글, 페이징, 검색 등 실무에서 필요한 기능을 추가한다.

---

## 🎯 이 단계를 배우는 이유

### 기본 CRUD만으로는 부족하다

Step 2에서 만든 API는 동작하지만 실무에서는 부족합니다:
- ❌ 게시글 1000개를 한 번에 조회? (느림)
- ❌ 특정 게시글을 찾으려면? (검색 기능 없음)
- ❌ 댓글 기능은? (추가 Entity 필요)

### 프론트엔드에서 본 것들

```javascript
// 프론트엔드에서 이미 경험한 기능들
<InfiniteScroll />      // 페이징
<SearchBar />           // 검색
<CommentList />         // 댓글
```

이제 백엔드에서 이런 기능의 **데이터를 제공하는 API**를 만들 차례입니다.

---

## 💡 핵심 개념

### 1. 페이징 (Pagination)

#### 왜 페이징이 필요한가?

```
게시글 10,000개 한 번에 조회
→ 데이터 전송량 10MB
→ 프론트엔드 렌더링 느림
→ 사용자 경험 나쁨

페이징: 10개씩 조회
→ 데이터 전송량 10KB
→ 빠름
→ 사용자 경험 좋음
```

#### 프론트엔드 비유

```javascript
// 무한 스크롤, 페이지네이션 컴포넌트
function PostList() {
    const [page, setPage] = useState(0);
    const { data } = useFetch(`/api/posts?page=${page}&size=10`);
    
    return (
        <>
            {data.content.map(post => <PostItem post={post} />)}
            <Pagination 
                total={data.totalPages} 
                current={page}
                onChange={setPage}
            />
        </>
    );
}
```

#### 스프링부트의 페이징

```java
// Page 객체 구조
{
    "content": [...],           // 실제 데이터
    "totalElements": 100,       // 전체 개수
    "totalPages": 10,           // 전체 페이지 수
    "size": 10,                 // 페이지 크기
    "number": 0,                // 현재 페이지 (0부터 시작)
    "first": true,              // 첫 페이지 여부
    "last": false               // 마지막 페이지 여부
}
```

---

### 2. 검색 (Search)

#### JPA Query Methods

메서드 이름만으로 쿼리 자동 생성!

```java
// 메서드 이름         →  생성되는 SQL
findByTitle()          →  WHERE title = ?
findByTitleContaining() →  WHERE title LIKE %?%
findByContentContaining() → WHERE content LIKE %?%
findByTitleAndContent() →  WHERE title = ? AND content = ?
```

#### 프론트엔드 비유

```javascript
// Array 메서드처럼 직관적
posts.filter(post => post.title.includes('검색어'))

// JPA도 비슷
postRepository.findByTitleContaining('검색어')
```

---

### 3. DTO 패턴 (Data Transfer Object)

#### Entity를 직접 반환하면 안 되는 이유

```java
// Entity 직접 반환 (나쁜 예)
@GetMapping
public List<Post> list() {
    return postService.findAll();
}
```

**문제점**:
1. **순환 참조**: Post → Board → Posts → Board... (무한 루프)
2. **민감한 정보 노출**: 비밀번호 같은 필드도 전부 노출
3. **성능 문제**: 연관된 모든 Entity 조회 (N+1 문제)
4. **API 변경 어려움**: Entity 변경 시 API 응답도 변경됨

#### DTO 사용 (좋은 예)

```java
// DTO: API 응답 전용 객체
@Data
public class PostDTO {
    private Long id;
    private String title;
    private String content;
    private String boardName;  // Board 전체 대신 이름만
    private int replyCount;    // 댓글 개수만
    
    // Entity → DTO 변환
    public static PostDTO from(Post post) {
        PostDTO dto = new PostDTO();
        dto.setId(post.getId());
        dto.setTitle(post.getTitle());
        dto.setContent(post.getContent());
        dto.setBoardName(post.getBoard().getName());
        dto.setReplyCount(post.getReplies().size());
        return dto;
    }
}
```

**장점**:
- 필요한 데이터만 선택적으로 반환
- 순환 참조 방지
- API 스펙 명확화

#### 프론트엔드 비유

```javascript
// 백엔드 DB 데이터 (Entity)
const user = {
    id: 1,
    email: 'user@example.com',
    password: 'hashed_password',  // 민감 정보
    address: {...},
    orders: [...]
};

// 프론트에 보내는 데이터 (DTO)
const userResponse = {
    id: 1,
    email: 'user@example.com',
    // password는 제외
    orderCount: user.orders.length  // 개수만
};
```

---

## 🛠️ 최소 구현 코드

### 1. 댓글 Entity 추가

```java
// src/main/java/com/project/board/model/Reply.java

package com.project.board.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Data
public class Reply {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String content;
    
    private String commenter;  // 작성자 (간단하게)
    
    @ManyToOne
    @JoinColumn(name = "post_id")
    private Post post;  // 댓글:게시글 = N:1
    
    private LocalDateTime createdAt;
    
    @PrePersist
    public void prePersist() {
        this.createdAt = LocalDateTime.now();
    }
}
```

```java
// Post Entity에 추가

import com.fasterxml.jackson.annotation.JsonIgnore;
import java.util.ArrayList;
import java.util.List;
import jakarta.persistence.OneToMany;

@Entity
@Data
public class Post {
    // 기존 필드들...
    
    @OneToMany(mappedBy = "post")  // Reply Entity의 post 필드와 매핑
    @JsonIgnore  // 순환 참조 방지
    private List<Reply> replies = new ArrayList<>();
}
```

**주의**: `mappedBy = "post"`는 Reply Entity에서 Post를 참조하는 필드명과 일치해야 합니다.

---

### 2. 페이징 구현

#### 📝 구현 순서 (중요!)

페이징 기능을 구현할 때는 **아래에서 위로** 순서대로 작성합니다:

```
1. Repository (데이터 접근) 
   ↓
2. Service (비즈니스 로직)
   ↓
3. Controller (API 엔드포인트)
```

**왜 이 순서인가?**
- Repository가 없으면 Service가 동작하지 않음
- Service가 없으면 Controller가 동작하지 않음
- **의존성 방향**: Controller → Service → Repository

#### Step 1: Repository 확인

```java
// PostRepository는 이미 JpaRepository 상속
// → Page 메서드 자동 제공
```

**JpaRepository가 자동 제공하는 페이징 메서드**:
- `Page<T> findAll(Pageable pageable)` - 페이징 전체 조회
- `Page<T> findAll(Specification<T> spec, Pageable pageable)` - 조건부 페이징

**현재 PostRepository**:
```java
// src/main/java/com/project/board/repository/PostRepository.java

@Repository
public interface PostRepository extends JpaRepository<Post, Long> {
    // JpaRepository가 이미 findAll(Pageable) 메서드를 제공하므로
    // 별도로 선언하지 않아도 사용 가능!
}
```

**추가 메서드가 필요한 경우** (예: 게시판별 페이징):
```java
public interface PostRepository extends JpaRepository<Post, Long> {
    // 게시판별 페이징 조회 (JPA Query Method)
    Page<Post> findByBoardId(Long boardId, Pageable pageable);
}
```

#### Step 2: Service에 페이징 메서드 추가

**기존 Service 코드 확인**:
```java
// 현재 PostService.java
public List<Post> findAll() {
    return postRepository.findAll();  // 전체 조회 (List 반환)
}
```

**페이징 메서드 추가** (기존 메서드는 유지):
```java
// src/main/java/com/project/board/service/PostService.java

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
// ... 기존 import들 ...

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PostService {
    
    private final PostRepository postRepository;
    
    // 기존 메서드 유지 (List 반환)
    public List<Post> findAll() {
        return postRepository.findAll();
    }
    
    // ✅ 새로 추가: 페이징 조회 (Page 반환)
    public Page<Post> findAll(Pageable pageable) {
        return postRepository.findAll(pageable);
    }
    
    // ✅ 선택사항: 게시판별 페이징 조회
    public Page<Post> findByBoardId(Long boardId, Pageable pageable) {
        return postRepository.findByBoardId(boardId, pageable);
    }
    
    // 기존 메서드들도 유지 (findById, save, update, delete 등)
}
```

**주의사항**:
- ✅ 기존 `findAll()` 메서드는 그대로 유지 (하위 호환성)
- ✅ 새로운 `findAll(Pageable pageable)` 메서드 추가 (오버로딩)
- ✅ 메서드 이름이 같지만 파라미터가 다르면 다른 메서드로 인식됨 (Java 오버로딩)

#### Step 3: Controller에 페이징 엔드포인트 추가

**기존 Controller 코드 확인**:
```java
// 현재 PostController.java
@GetMapping
public ResponseEntity<List<Post>> list() {
    List<Post> posts = postService.findAll();
    return ResponseEntity.ok(posts);
}
```

**선택지 1: 기존 메서드를 페이징으로 변경** (권장)
```java
// src/main/java/com/project/board/controller/PostController.java

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
// ... 기존 import들 ...

@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostController {
    
    private final PostService postService;
    
    // ✅ 기존 메서드를 페이징으로 변경
    // GET /api/posts?page=0&size=10&sort=id,desc
    @GetMapping
    public ResponseEntity<Page<Post>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "id") String sortBy,
            @RequestParam(defaultValue = "DESC") String direction) {
        
        // Sort.Direction 변환
        Sort.Direction sortDirection = Sort.Direction.fromString(direction);
        
        // Pageable 객체 생성 (페이지 번호, 크기, 정렬)
        Pageable pageable = PageRequest.of(page, size, 
                                            Sort.by(sortDirection, sortBy));
        
        // Service 호출 (이제 Page 반환)
        Page<Post> posts = postService.findAll(pageable);
        return ResponseEntity.ok(posts);
    }
    
    // 기존 메서드들 유지 (get, create, update, delete)
}
```

**선택지 2: 페이징 전용 엔드포인트 추가** (기존 API 유지)
```java
@GetMapping
public ResponseEntity<List<Post>> list() {
    // 기존 전체 조회 유지
    List<Post> posts = postService.findAll();
    return ResponseEntity.ok(posts);
}

@GetMapping("/paged")  // 새로운 엔드포인트
public ResponseEntity<Page<Post>> listPaged(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(defaultValue = "id") String sortBy,
        @RequestParam(defaultValue = "DESC") String direction) {
    
    Sort.Direction sortDirection = Sort.Direction.fromString(direction);
    Pageable pageable = PageRequest.of(page, size, 
                                        Sort.by(sortDirection, sortBy));
    Page<Post> posts = postService.findAll(pageable);
    return ResponseEntity.ok(posts);
}
```

**각 코드 라인 설명**:
```java
// 1. URL 파라미터 받기
@RequestParam(defaultValue = "0") int page  // 페이지 번호 (0부터 시작)
@RequestParam(defaultValue = "10") int size // 페이지 크기 (한 페이지당 개수)
@RequestParam(defaultValue = "id") String sortBy  // 정렬 기준 필드
@RequestParam(defaultValue = "DESC") String direction  // 정렬 방향

// 2. Sort.Direction 변환
Sort.Direction sortDirection = Sort.Direction.fromString(direction);
// "DESC" → Sort.Direction.DESC
// "ASC" → Sort.Direction.ASC

// 3. Pageable 객체 생성
Pageable pageable = PageRequest.of(page, size, Sort.by(sortDirection, sortBy));
// PageRequest.of(0, 10, Sort.by(DESC, "id"))
// → 0번째 페이지, 10개씩, id 기준 내림차순

// 4. Service 호출
Page<Post> posts = postService.findAll(pageable);
// Page 객체에는 데이터뿐만 아니라 페이징 정보도 포함됨
```

#### Step 4: 테스트

**Postman 테스트**:
```
# 기본 페이징 (파라미터 없으면 기본값 사용)
GET http://localhost:8080/api/posts
→ page=0, size=10, sort=id, direction=DESC

# 첫 페이지, 5개씩
GET http://localhost:8080/api/posts?page=0&size=5

# 두 번째 페이지, 5개씩
GET http://localhost:8080/api/posts?page=1&size=5

# 정렬 옵션 변경
GET http://localhost:8080/api/posts?page=0&size=10&sort=id&direction=DESC
GET http://localhost:8080/api/posts?page=0&size=10&sort=title&direction=ASC
```

**응답 예시**:
```json
{
  "content": [
    {"id": 10, "title": "게시글 10", ...},
    {"id": 9, "title": "게시글 9", ...},
    ...
  ],
  "totalElements": 100,    // 전체 게시글 수
  "totalPages": 10,        // 전체 페이지 수
  "size": 10,              // 페이지 크기
  "number": 0,             // 현재 페이지 번호
  "first": true,           // 첫 페이지 여부
  "last": false,           // 마지막 페이지 여부
  "numberOfElements": 10   // 현재 페이지의 요소 개수
}
```

**참고**: Post Entity에 `createdAt` 필드를 추가하면 `sort=createdAt&direction=DESC`도 사용 가능합니다.

---

#### 📌 전체 구현 순서 요약

```
1. Repository 확인
   → JpaRepository가 이미 findAll(Pageable) 제공
   → 필요시 커스텀 메서드 추가 (findByBoardId 등)

2. Service에 페이징 메서드 추가
   → Page<Post> findAll(Pageable pageable) 추가
   → 기존 List<Post> findAll() 유지 (선택)

3. Controller에 페이징 파라미터 추가
   → @RequestParam으로 page, size, sortBy, direction 받기
   → Pageable 객체 생성
   → Service 호출

4. 테스트
   → Postman으로 다양한 파라미터 조합 테스트
```

---

### 3. 검색 기능 구현

#### Repository에 검색 메서드 추가
```java
// src/main/java/com/project/board/repository/PostRepository.java

public interface PostRepository extends JpaRepository<Post, Long> {
    
    // 게시판별 조회 (페이징)
    Page<Post> findByBoardId(Long boardId, Pageable pageable);
    
    // 제목으로 검색
    Page<Post> findByTitleContaining(String keyword, Pageable pageable);
    
    // 내용으로 검색
    Page<Post> findByContentContaining(String keyword, Pageable pageable);
    
    // 제목 또는 내용으로 검색
    Page<Post> findByTitleContainingOrContentContaining(
        String titleKeyword, 
        String contentKeyword, 
        Pageable pageable
    );
}
```

#### Service에 검색 메서드 추가
```java
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PostService {
    
    private final PostRepository postRepository;
    
    // 검색
    public Page<Post> search(String keyword, Pageable pageable) {
        return postRepository.findByTitleContainingOrContentContaining(
            keyword, keyword, pageable
        );
    }
}
```

#### Controller에 검색 엔드포인트 추가
```java
@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostController {
    
    private final PostService postService;
    
    // GET /api/posts/search?keyword=검색어&page=0&size=10
    @GetMapping("/search")
    public ResponseEntity<Page<Post>> search(
            @RequestParam String keyword,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<Post> posts = postService.search(keyword, pageable);
        return ResponseEntity.ok(posts);
    }
}
```

---

### 4. DTO 패턴 적용

#### PostDTO 생성
```java
// src/main/java/com/project/board/dto/PostDTO.java

package com.project.board.dto;

import com.project.board.model.Post;
import lombok.Builder;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@Builder
public class PostDTO {
    private Long id;
    private String title;
    private String content;
    private String boardName;
    private int replyCount;
    private LocalDateTime createdAt;
    
    // Entity → DTO 변환
    public static PostDTO from(Post post) {
        return PostDTO.builder()
                .id(post.getId())
                .title(post.getTitle())
                .content(post.getContent())
                .boardName(post.getBoard() != null ? 
                          post.getBoard().getName() : null)
                .replyCount(post.getReplies() != null ? 
                           post.getReplies().size() : 0)
                .createdAt(post.getCreatedAt())  // Post Entity에 createdAt 필드가 있는 경우
                .build();
    }
```

**주의**: Post Entity에 `createdAt` 필드가 없는 경우, 이 줄을 제거하거나 `null`로 설정해야 합니다.

#### Controller에서 DTO 사용
```java
import com.project.board.dto.PostDTO;
import org.springframework.data.domain.Page;

@RestController
@RequestMapping("/api/posts")
@RequiredArgsConstructor
public class PostController {
    
    private final PostService postService;
    
    // DTO로 변환해서 반환
    @GetMapping
    public ResponseEntity<Page<PostDTO>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<Post> posts = postService.findAll(pageable);
        
        // Entity → DTO 변환
        Page<PostDTO> postDTOs = posts.map(PostDTO::from);
        
        return ResponseEntity.ok(postDTOs);
    }
}
```

---

### 5. 예외 처리 개선

#### 커스텀 예외 생성
```java
// src/main/java/com/project/board/exception/ResourceNotFoundException.java

package com.project.board.exception;

public class ResourceNotFoundException extends RuntimeException {
    public ResourceNotFoundException(String message) {
        super(message);
    }
}
```

#### 전역 예외 처리
```java
// src/main/java/com/project/board/exception/GlobalExceptionHandler.java

package com.project.board.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleNotFound(
            ResourceNotFoundException e) {
        
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("success", false);
        errorResponse.put("message", e.getMessage());
        errorResponse.put("timestamp", LocalDateTime.now());
        
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                             .body(errorResponse);
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleException(Exception e) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("success", false);
        errorResponse.put("message", "서버 오류가 발생했습니다.");
        errorResponse.put("timestamp", LocalDateTime.now());
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                             .body(errorResponse);
    }
}
```

#### Service에서 사용
```java
@Service
@RequiredArgsConstructor
public class PostService {
    
    private final PostRepository postRepository;
    
    public Post findById(Long id) {
        return postRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException(
                    "게시글을 찾을 수 없습니다. ID: " + id
                ));
    }
}
```

---

## 📝 실습 가이드

### Step 1: Reply Entity 추가
1. `Reply.java` 생성
2. `Post`에 `replies` 필드 추가
3. `ReplyRepository`, `ReplyService`, `ReplyController` 생성

### Step 2: 페이징 테스트
```
# 10개 게시글 생성 (Postman에서 반복)
POST /api/posts (10번)

# 페이징 조회
GET /api/posts?page=0&size=5
GET /api/posts?page=1&size=5
```

### Step 3: 검색 테스트
```
# 게시글 생성 (제목 다양하게)
POST /api/posts {"title": "스프링부트", ...}
POST /api/posts {"title": "자바 프로그래밍", ...}
POST /api/posts {"title": "리액트", ...}

# 검색
GET /api/posts/search?keyword=스프링
GET /api/posts/search?keyword=자바
```

### Step 4: DTO 적용
1. `PostDTO.java` 생성
2. Controller에서 DTO 변환
3. 순환 참조 해결 확인

### Step 5: 예외 처리 테스트
```
# 존재하지 않는 게시글 조회
GET /api/posts/999
→ 404 Not Found + 명확한 에러 메시지
```

---

## 🎓 다음 단계로

### 이 단계에서 배운 것
- ✅ 페이징 (Page, Pageable)
- ✅ 검색 (JPA Query Methods)
- ✅ DTO 패턴 (Entity 보호)
- ✅ 댓글 기능 (1:N 관계 추가)
- ✅ 전역 예외 처리 (@RestControllerAdvice)

### 아직 부족한 것
- ❌ 사용자 인증 (누가 작성했는지)
- ❌ 권한 관리 (작성자만 수정/삭제)
- ❌ 보안 (비밀번호 암호화)

### 다음 단계 예고: Step 4 - 인증 및 권한 관리

**Step 4에서 배울 것**:
1. **Spring Security**: 스프링 보안 프레임워크
2. **JWT (JSON Web Token)**: 토큰 기반 인증
3. **회원가입/로그인**: User Entity, AuthController
4. **권한 기반 접근 제어**: ROLE_USER, ROLE_ADMIN
5. **작성자 권한 체크**: 본인만 수정/삭제

**예제 API**:
```
POST /api/auth/register  - 회원가입
POST /api/auth/login     - 로그인 (JWT 발급)
GET  /api/posts          - 인증 필요
POST /api/posts          - 인증 + 권한 필요
```

---

## 💡 핵심 정리

### 페이징이 필요한 이유
- 대량 데이터를 한 번에 조회하면 성능 저하
- 프론트엔드 렌더링 부담
- 네트워크 트래픽 증가

### DTO가 필요한 이유
- Entity 직접 노출은 위험 (민감 정보, 순환 참조)
- API 스펙과 Entity를 분리
- 필요한 데이터만 선택적으로 반환

### 검색 기능 구현 방법
- 간단한 검색: JPA Query Methods
- 복잡한 검색: QueryDSL (다음 단계에서)

---

**준비되셨나요? Step 4로 넘어가서 사용자 인증을 구현해봅시다! 🚀**

```bash
# 다음 문서
dont_upload/Step_04_인증_권한_관리.md
```

