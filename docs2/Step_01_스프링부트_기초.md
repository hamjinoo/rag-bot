# Step 1: 스프링부트 기초

> **목표**: 스프링부트가 무엇인지 이해하고, 첫 번째 API를 만들어본다.

---

## 🎯 이 단계를 배우는 이유

### 왜 스프링부트인가?

백엔드 개발에서 **스프링부트는 자바 진영의 React 같은 존재**입니다.

- React가 프론트엔드 개발을 쉽게 만들어주듯
- 스프링부트는 백엔드 API 개발을 쉽게 만들어줍니다

### 프론트엔드 관점에서 이해하기

```
프론트엔드                  백엔드
------------------         ------------------
React Component      ←→    Spring Controller
Redux/Context        ←→    Spring Container (IoC)
npm/yarn             ←→    Maven/Gradle
package.json         ←→    pom.xml/build.gradle
useState/useEffect   ←→    Service/Repository
API 호출 (fetch)     ←→    API 제공 (@RestController)
```

### 실무에서 왜 필요한가?

1. **프론트엔드 개발자의 성장**

   - 프론트만 개발하면: "API가 왜 느려요?" (문의만 가능)
   - 백엔드도 알면: "쿼리를 최적화하거나 캐싱을 추가하면 어떨까요?" (제안 가능)

2. **협업 능력 향상**

   - 백엔드 개발자와 같은 언어로 소통
   - API 설계 단계부터 참여 가능

3. **풀스택 개발자로 성장**
   - 작은 프로젝트는 혼자서 개발 가능
   - 더 높은 연봉과 기회

---

## 💡 핵심 개념

### 1. 스프링 프레임워크 vs 스프링부트

#### 스프링 프레임워크 (Spring Framework)

- 자바 애플리케이션 개발을 위한 **거대한 프레임워크**
- 설정이 복잡함 (XML 파일 수십 개)
- 학습 곡선이 가파름

#### 스프링부트 (Spring Boot)

- 스프링 프레임워크를 **쉽게 사용**할 수 있도록 만든 도구
- 설정을 자동화 (Auto Configuration)
- 내장 서버 제공 (Tomcat)
- **프론트엔드 비유**: Create React App (CRA)처럼 복잡한 설정 없이 바로 시작

```
Spring Framework = React (직접 모든 설정)
Spring Boot      = Create React App (설정 자동화)
```

---

### 2. IoC (Inversion of Control) - 제어의 역전

**핵심 개념**: "객체를 내가 만들지 않고, 스프링이 만들어서 주입해준다"

#### 전통적인 방식 (Without IoC)

```java
// 내가 직접 객체 생성
public class PostController {
    private PostService postService = new PostService();  // 직접 생성
    private Logger logger = new Logger();                 // 직접 생성
}
```

**문제점**:

- 테스트하기 어려움
- 객체 간 결합도가 높음
- 변경이 어려움

#### 스프링 방식 (With IoC)

```java
// 스프링이 객체를 만들어서 주입
@RestController
public class PostController {
    private final PostService postService;  // 스프링이 주입

    // 생성자를 통해 주입받음
    public PostController(PostService postService) {
        this.postService = postService;
    }
}
```

**장점**:

- 테스트하기 쉬움 (Mock 객체 주입 가능)
- 객체 간 결합도가 낮음
- 변경이 쉬움

#### 프론트엔드 비유: React Context / Provider

```jsx
// React Context - Provider가 값을 주입
function App() {
  return (
    <ThemeProvider value={theme}>
      <UserProvider value={user}>
        <HomePage /> {/* 자식 컴포넌트가 Context 값을 받음 */}
      </UserProvider>
    </ThemeProvider>
  );
}

// HomePage는 직접 만들지 않고 useContext로 받음
function HomePage() {
  const theme = useContext(ThemeContext); // Provider가 주입
  const user = useContext(UserContext); // Provider가 주입
}
```

**스프링도 같은 방식**:

- `Provider` = **Spring Container (IoC Container)**
- `useContext` = **의존성 주입 (Dependency Injection)**

---

### 3. DI (Dependency Injection) - 의존성 주입

**의존성**: 어떤 객체가 다른 객체를 사용하는 것

```java
public class PostController {
    private PostService postService;  // PostController는 PostService에 의존
}
```

**주입 방식 3가지**

#### 방식 1: 생성자 주입 (권장)

```java
@RestController
public class PostController {
    private final PostService postService;  // final 사용 가능

    public PostController(PostService postService) {
        this.postService = postService;
    }
}
```

**장점**: 불변성 보장, 테스트 용이, 순환 참조 방지

#### 방식 2: 필드 주입 (비권장)

```java
@RestController
public class PostController {
    @Autowired  // 스프링이 자동으로 주입
    private PostService postService;
}
```

**단점**: final 사용 불가, 테스트 어려움

#### 방식 3: Setter 주입 (선택적 의존성)

```java
@RestController
public class PostController {
    private PostService postService;

    @Autowired
    public void setPostService(PostService postService) {
        this.postService = postService;
    }
}
```

**사용 시기**: 선택적으로 주입할 때만

---

### 4. 스프링 컨테이너와 빈 (Bean)

#### 스프링 컨테이너

- 객체(빈)를 생성하고 관리하는 곳
- **프론트엔드 비유**: Redux Store, React Context

#### 빈 (Bean)

- 스프링 컨테이너가 관리하는 객체
- `@Component`, `@Service`, `@Repository`, `@Controller` 등으로 등록

```java
@Service  // 이 클래스를 빈으로 등록
public class PostService {
    // 스프링이 자동으로 객체 생성
}
```

#### 동작 과정

```
1. 애플리케이션 시작
   ↓
2. 스프링이 @Service, @Controller 등을 찾음
   ↓
3. 객체를 생성해서 스프링 컨테이너에 저장
   ↓
4. 필요한 곳에 자동으로 주입
```

**프론트엔드 비유**:

```jsx
// Provider가 값을 저장하고 제공
<Provider store={store}>
  {" "}
  {/* 스프링 컨테이너 */}
  <App />
</Provider>;

// useSelector로 꺼내 씀
const user = useSelector((state) => state.user); // DI
```

---

### 5. 어노테이션 (Annotation)

자바의 메타데이터, 클래스나 메서드에 추가 정보를 제공

#### 주요 어노테이션

| 어노테이션               | 역할              | 프론트엔드 비유        |
| ------------------------ | ----------------- | ---------------------- |
| `@SpringBootApplication` | 스프링부트 시작점 | `ReactDOM.render()`    |
| `@RestController`        | REST API 컨트롤러 | API Route Handler      |
| `@Service`               | 비즈니스 로직     | Service 클래스         |
| `@Repository`            | 데이터베이스 접근 | API 호출 함수          |
| `@GetMapping`            | HTTP GET 요청     | `app.get()` (Express)  |
| `@PostMapping`           | HTTP POST 요청    | `app.post()` (Express) |
| `@RequestBody`           | JSON → 객체 변환  | `req.body`             |
| `@PathVariable`          | URL 파라미터      | `req.params`           |

---

## 🛠️ 최소 구현 코드

### 1. 프로젝트 생성 (Spring Initializr)

1. **웹사이트 접속**: https://start.spring.io/
2. **설정**:
   - Project: Gradle - Groovy
   - Language: Java
   - Spring Boot: 3.2.x (최신 안정 버전)
   - Packaging: Jar
   - Java: 17
3. **Dependencies 추가**:
   - Spring Web
   - Spring Data JPA
   - H2 Database
   - Lombok
4. **GENERATE** 버튼 클릭 → 압축 파일 다운로드
5. 압축 해제 후 IntelliJ로 열기

---

### 2. 프로젝트 구조 이해

```
src/
├── main/
│   ├── java/
│   │   └── com.project.board/
│   │       ├── BoardApplication.java        # 시작점
│   │       ├── controller/                  # API 엔드포인트
│   │       ├── service/                     # 비즈니스 로직
│   │       ├── repository/                  # 데이터베이스 접근
│   │       └── model/                       # 엔티티 (데이터 구조)
│   └── resources/
│       └── application.properties           # 설정 파일
└── test/                                    # 테스트 코드
```

**프론트엔드 비유**:

```
src/
├── components/        ←→  controller/
├── services/          ←→  service/
├── api/               ←→  repository/
├── types/             ←→  model/
└── config/            ←→  resources/
```

---

### 3. 메인 애플리케이션 클래스

```java
// src/main/java/com/project/board/BoardApplication.java

package com.project.board;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication  // 스프링부트의 시작점
public class BoardApplication {

    public static void main(String[] args) {
        SpringApplication.run(BoardApplication.java, args);
        // 서버 시작: http://localhost:8080
    }
}
```

**`@SpringBootApplication`이 하는 일**:

1. 컴포넌트 스캔 (어노테이션 달린 클래스 찾기)
2. 자동 설정 활성화
3. 추가 빈 등록 가능

---

### 4. 첫 번째 REST API 만들기

```java
// src/main/java/com/project/board/controller/HelloController.java

package com.project.board.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController  // 이 클래스는 REST API 컨트롤러
@RequestMapping("/api")  // 기본 경로: /api
public class HelloController {

    // GET /api/hello
    @GetMapping("/hello")
    public String hello() {
        return "Hello, Spring Boot!";
    }

    // GET /api/hello/board
    @GetMapping("/hello/board")
    public String helloBoard() {
        return "Welcome to Board API!";
    }
}
```

**어노테이션 설명**:

- `@RestController`: 이 클래스가 REST API를 제공한다고 선언
- `@RequestMapping("/api")`: 이 컨트롤러의 모든 메서드는 `/api`로 시작
- `@GetMapping("/hello")`: HTTP GET 요청을 처리

**프론트엔드 비유**:

```javascript
// Express.js
app.get("/api/hello", (req, res) => {
  res.send("Hello, Spring Boot!");
});
```

---

### 5. JSON 응답 반환하기

```java
// src/main/java/com/project/board/controller/HelloController.java

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class HelloController {

    // JSON 응답 반환
    @GetMapping("/info")
    public Map<String, Object> getInfo() {
        Map<String, Object> info = new HashMap<>();
        info.put("name", "Board API");
        info.put("version", "1.0.0");
        info.put("status", "running");
        return info;  // 자동으로 JSON 변환
    }
}
```

**응답 예시**:

```json
{
  "name": "Board API",
  "version": "1.0.0",
  "status": "running"
}
```

**스프링부트의 마법**:

- Map, 객체를 반환하면 자동으로 JSON 변환
- Jackson 라이브러리가 자동으로 처리
- `@RestController` 덕분에 `@ResponseBody` 생략 가능

---

### 6. 객체로 응답하기 (DTO 패턴)

```java
// src/main/java/com/project/board/dto/ApiInfo.java

package com.project.board.dto;

public class ApiInfo {
    private String name;
    private String version;
    private String status;

    // 생성자
    public ApiInfo(String name, String version, String status) {
        this.name = name;
        this.version = version;
        this.status = status;
    }

    // Getter (필수: JSON 변환에 필요)
    public String getName() { return name; }
    public String getVersion() { return version; }
    public String getStatus() { return status; }
}
```

```java
// Controller에서 사용

@GetMapping("/info")
public ApiInfo getInfo() {
    return new ApiInfo("Board API", "1.0.0", "running");
}
```

**Lombok을 사용하면 더 간단**:

```java
import lombok.AllArgsConstructor;
import lombok.Data;

@Data  // Getter, Setter, toString 등 자동 생성
@AllArgsConstructor  // 모든 필드를 받는 생성자 자동 생성
public class ApiInfo {
    private String name;
    private String version;
    private String status;
}
```

---

## 📝 실습 가이드

### Step 1: 프로젝트 생성

1. https://start.spring.io/ 접속
2. 위 설정대로 프로젝트 생성
3. 다운로드 후 압축 해제
4. IntelliJ에서 `build.gradle` 열기

### Step 2: 의존성 확인

```gradle
// build.gradle

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'com.h2database:h2'
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
}
```

### Step 3: application.properties 설정

```properties
# src/main/resources/application.properties

# 서버 포트 (기본값: 8080)
server.port=8080

# H2 Database 설정
spring.h2.console.enabled=true
spring.datasource.url=jdbc:h2:mem:testdb
spring.datasource.driverClassName=org.h2.Driver
```

### Step 4: HelloController 생성

위 코드대로 `HelloController.java` 생성

### Step 5: 애플리케이션 실행

1. `BoardApplication.java` 우클릭 → Run
2. 콘솔에서 "Started BoardApplication" 확인
3. 브라우저에서 http://localhost:8080/api/hello 접속

### Step 6: 테스트

브라우저 또는 Postman에서 테스트:

```
GET http://localhost:8080/api/hello
→ "Hello, Spring Boot!"

GET http://localhost:8080/api/hello/board
→ "Welcome to Board API!"

GET http://localhost:8080/api/info
→ {"name":"Board API","version":"1.0.0","status":"running"}
```

---

## 🎓 다음 단계로

### 이 단계에서 배운 것

- ✅ 스프링부트 프로젝트 생성
- ✅ IoC와 DI 개념 이해
- ✅ `@RestController`, `@GetMapping` 사용법
- ✅ 첫 번째 REST API 만들기
- ✅ JSON 응답 반환하기

### 아직 부족한 것

- ❌ 데이터베이스 연동
- ❌ 데이터 저장/조회 (CRUD)
- ❌ 복잡한 비즈니스 로직

### 다음 단계 예고: Step 2 - 기본 게시판 API

**Step 2에서 배울 것**:

1. **Entity**: 데이터베이스 테이블 정의
2. **Repository**: 데이터베이스 접근
3. **Service**: 비즈니스 로직
4. **Controller**: REST API 완성
5. **CRUD 전체 구현**: 게시글 생성, 조회, 수정, 삭제

**예제 API**:

```
POST   /api/posts       - 게시글 생성
GET    /api/posts       - 게시글 목록
GET    /api/posts/{id}  - 게시글 상세
PUT    /api/posts/{id}  - 게시글 수정
DELETE /api/posts/{id}  - 게시글 삭제
```

---

## 💡 자주 묻는 질문

### Q1: @RestController vs @Controller 차이는?

**A**: `@RestController` = `@Controller` + `@ResponseBody`

- `@Controller`: HTML 뷰를 반환 (Thymeleaf 등)
- `@RestController`: JSON/XML을 반환 (REST API용)

### Q2: Lombok이 뭔가요?

**A**: 반복적인 코드(Getter, Setter 등)를 자동 생성해주는 라이브러리

```java
// Lombok 없이
public class User {
    private String name;
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}

// Lombok 사용
@Data
public class User {
    private String name;
}
```

### Q3: 포트 8080이 이미 사용 중이라고 나와요

**A**: `application.properties`에서 포트 변경

```properties
server.port=8081
```

### Q4: 브라우저에서 404 에러가 나요

**A**: URL 확인

- 맞는 URL: `http://localhost:8080/api/hello`
- 틀린 URL: `http://localhost:8080/hello` (api 빠짐)

---

**준비되셨나요? Step 2로 넘어가서 실제 데이터베이스를 연동해봅시다! 🚀**

```bash
# 다음 문서
dont_upload/Step_02_기본_게시판_API.md
```
