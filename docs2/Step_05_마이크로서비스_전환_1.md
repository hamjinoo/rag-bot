# Step 5: 마이크로서비스 전환 - 1

> **목표**: 모놀리식 애플리케이션을 마이크로서비스 아키텍처로 분리하고, Service Discovery를 구현한다.

---

## 🎯 이 단계를 배우는 이유

### 모놀리식의 한계

지금까지 만든 애플리케이션은 **모놀리식(Monolithic)**:
- 모든 기능이 하나의 프로젝트에 포함
- 작은 수정에도 전체 재배포 필요
- 특정 기능만 확장 불가능
- 한 부분의 장애가 전체 시스템 영향

### 마이크로서비스의 장점

```
모놀리식                         마이크로서비스
[User + Board + Post]      →     [User Service]
                                  [Board Service]
                                  [Post Service]

- 전체 재배포                      - 개별 배포
- 전체 확장                       - 필요한 서비스만 확장
- 기술 스택 고정                   - 서비스별 다른 기술 사용 가능
```

### 프론트엔드 비유: Micro Frontend

```javascript
// 모놀리식 프론트엔드
<App>
  <Header />
  <UserProfile />
  <Board />
  <Footer />
</App>

// 마이크로 프론트엔드
http://user.example.com     → User 앱
http://board.example.com    → Board 앱
http://admin.example.com    → Admin 앱
```

---

## 💡 핵심 개념

### 1. 마이크로서비스 아키텍처 (MSA)

#### 정의
- 애플리케이션을 **작고 독립적인 서비스**로 분리
- 각 서비스는 **자체 데이터베이스** 보유
- 서비스 간 **API 통신** (HTTP/gRPC)

#### 분리 기준: 도메인 주도 설계 (DDD)

```
게시판 시스템 분리:

1. User Service
   - 회원가입, 로그인, 프로필 관리
   - user_db

2. Board Service
   - 게시판 목록, 게시판 생성
   - board_db

3. Post Service
   - 게시글 CRUD, 검색
   - post_db

4. Comment Service
   - 댓글 CRUD
   - comment_db
```

---

### 2. Service Discovery (서비스 디스커버리)

#### 문제 상황

```
Post Service가 User Service를 호출해야 함
→ User Service의 IP 주소는?
→ 서버가 여러 개면? (로드 밸런싱)
→ 서버가 추가/제거되면?
```

#### 해결: Eureka Server

```
[Eureka Server]  ← 서비스 등록소
     ↑
     ├── User Service (localhost:8081) 등록
     ├── Board Service (localhost:8082) 등록
     └── Post Service (localhost:8083) 등록

Post Service: "User Service 어디 있어요?"
Eureka: "localhost:8081에 있어요!"
```

**프론트엔드 비유**: DNS, Service Mesh
- DNS처럼 서비스 이름 → IP 주소로 변환
- 서비스가 추가/제거되면 자동 반영

---

### 3. Config Server (중앙 설정 관리)

#### 문제 상황

```
마이크로서비스가 10개
각각 application.properties 파일 관리
→ DB 비밀번호 변경 시 10개 파일 수정
→ 재배포 10번
```

#### 해결: Config Server

```
[Config Server]  ← Git Repository
     ↓ 설정 파일 가져오기
[각 마이크로서비스]
```

---

## 🛠️ 최소 구현 코드

### 1. 프로젝트 구조 변경

```
기존 (모놀리식):
board/
└── src/main/java/com/project/board/
    ├── controller/
    ├── service/
    ├── repository/
    └── model/

변경 (마이크로서비스):
board-system/
├── eureka-server/           # 서비스 디스커버리
├── config-server/           # 설정 서버
├── user-service/            # 사용자 서비스
├── board-service/           # 게시판 서비스
└── post-service/            # 게시글 서비스
```

---

### 2. Eureka Server 생성

#### 새 프로젝트 생성 (Spring Initializr)
- Dependencies: Eureka Server

#### build.gradle
```gradle
dependencies {
    implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-server'
}

dependencyManagement {
    imports {
        mavenBom "org.springframework.cloud:spring-cloud-dependencies:2023.0.0"
    }
}
```

#### EurekaServerApplication.java
```java
package com.project.eureka;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.server.EnableEurekaServer;

@SpringBootApplication
@EnableEurekaServer  // Eureka Server 활성화
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}
```

#### application.yml
```yaml
server:
  port: 8761  # Eureka 기본 포트

spring:
  application:
    name: eureka-server

eureka:
  client:
    register-with-eureka: false  # 자기 자신은 등록 안 함
    fetch-registry: false
  server:
    enable-self-preservation: false  # 개발 환경용
```

**실행 후 접속**: http://localhost:8761

---

### 3. User Service 분리

#### 새 프로젝트 생성
- Dependencies: Spring Web, JPA, H2, Eureka Discovery Client

#### build.gradle
```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client'
    runtimeOnly 'com.h2database:h2'
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
}

dependencyManagement {
    imports {
        mavenBom "org.springframework.cloud:spring-cloud-dependencies:2023.0.0"
    }
}
```

#### UserServiceApplication.java
```java
package com.project.user;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication
@EnableDiscoveryClient  // Eureka에 등록
public class UserServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
    }
}
```

#### application.yml
```yaml
server:
  port: 8081

spring:
  application:
    name: user-service  # 서비스 이름 (중요!)
  
  datasource:
    url: jdbc:h2:mem:userdb
    driver-class-name: org.h2.Driver
  
  jpa:
    hibernate:
      ddl-auto: create
    show-sql: true

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/  # Eureka Server 주소
```

#### 코드 이동
- User Entity, UserRepository, UserService, UserController
- Auth 관련 코드

---

### 4. Post Service 분리

#### application.yml
```yaml
server:
  port: 8082

spring:
  application:
    name: post-service
  
  datasource:
    url: jdbc:h2:mem:postdb
    driver-class-name: org.h2.Driver
  
  jpa:
    hibernate:
      ddl-auto: create
    show-sql: true

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
```

#### 코드 이동
- Post Entity, PostRepository, PostService, PostController
- Board Entity (Post와 연관)

---

### 5. 서비스 간 통신 (기본)

#### 문제: Post Service에서 User 정보 필요

```java
// Post 작성자 이름을 가져오려면?
// User Service API 호출 필요
```

#### 해결: RestTemplate (기본 방식)

```java
// PostService.java

@Service
@RequiredArgsConstructor
public class PostService {
    
    private final PostRepository postRepository;
    private final RestTemplate restTemplate;
    
    public PostDTO getPostWithAuthor(Long postId) {
        Post post = postRepository.findById(postId)
                .orElseThrow(() -> new RuntimeException("게시글 없음"));
        
        // User Service 호출
        String userServiceUrl = "http://user-service/api/users/" + post.getAuthorId();
        UserDTO author = restTemplate.getForObject(userServiceUrl, UserDTO.class);
        
        // DTO 생성
        PostDTO dto = PostDTO.from(post);
        dto.setAuthorName(author.getName());
        return dto;
    }
}
```

#### RestTemplate Bean 등록

```java
// PostServiceApplication.java

@SpringBootApplication
@EnableDiscoveryClient
public class PostServiceApplication {
    
    @Bean
    @LoadBalanced  // Eureka와 연동 (서비스 이름 → IP 변환)
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
    
    public static void main(String[] args) {
        SpringApplication.run(PostServiceApplication.class, args);
    }
}
```

**중요**: `@LoadBalanced` 덕분에 `http://user-service`가 실제 IP로 변환됨!

---

## 📝 실습 가이드

### Step 1: Eureka Server 실행
1. eureka-server 프로젝트 실행
2. http://localhost:8761 접속
3. "Instances currently registered" 확인 (아직 비어있음)

### Step 2: User Service 실행
1. user-service 프로젝트 실행
2. Eureka 대시보드 새로고침
3. "USER-SERVICE" 등록 확인

### Step 3: Post Service 실행
1. post-service 프로젝트 실행
2. Eureka 대시보드 새로고침
3. "POST-SERVICE" 등록 확인

### Step 4: 서비스 간 통신 테스트
```
# User 생성
POST http://localhost:8081/api/users
{
    "name": "홍길동",
    "email": "user@example.com"
}

# Post 생성 (authorId 포함)
POST http://localhost:8082/api/posts
{
    "title": "첫 게시글",
    "content": "내용",
    "authorId": 1
}

# Post 조회 (작성자 이름 포함)
GET http://localhost:8082/api/posts/1
→ 내부적으로 User Service 호출
```

---

## 🎓 다음 단계로

### 이 단계에서 배운 것
- ✅ 마이크로서비스 아키텍처 개념
- ✅ Eureka Server (Service Discovery)
- ✅ 서비스 분리 (User, Post)
- ✅ RestTemplate을 활용한 서비스 간 통신

### 아직 부족한 것
- ❌ API Gateway (단일 진입점)
- ❌ Feign Client (더 쉬운 통신)
- ❌ Circuit Breaker (장애 대응)
- ❌ 분산 트랜잭션

### 다음 단계: Step 6 - 마이크로서비스 전환 2

**Step 6에서 배울 것**:
1. **API Gateway**: 단일 진입점
2. **Feign Client**: 선언적 HTTP 클라이언트
3. **Circuit Breaker**: Resilience4j로 장애 대응
4. **분산 추적**: Spring Cloud Sleuth

---

**준비되셨나요? Step 6으로 넘어가서 API Gateway와 Feign Client를 배워봅시다! 🚀**

```bash
# 다음 문서
dont_upload/Step_06_마이크로서비스_전환_2.md
```

