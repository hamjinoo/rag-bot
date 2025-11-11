# Step 9: 모니터링 및 성능 최적화

> **목표**: 로깅, 성능 최적화, 캐싱을 통해 프로덕션 수준의 시스템을 만든다.

---

## 🎯 이 단계를 배우는 이유

### 배포 후 문제

```
배포 성공!
그런데...
- 어떤 API가 느린지 모름
- 에러가 나도 로그를 찾기 어려움
- 같은 데이터를 계속 DB에서 조회 (비효율)
```

### 모니터링의 필요성

```
"User Service가 느려요!"
→ 어떤 API?
→ 몇 초 걸림?
→ 어디서 병목?

모니터링 있으면:
GET /api/users → 평균 2초 (DB 쿼리 1.8초)
→ DB 쿼리 최적화 필요!
```

---

## 💡 핵심 개념

### 1. 로깅 (Logging)

#### 로그 레벨

```java
log.trace("상세 디버그 정보");       // 거의 안 씀
log.debug("디버그 정보");           // 개발 환경
log.info("일반 정보");              // 운영 환경 기본
log.warn("경고");                  // 주의 필요
log.error("에러", exception);      // 즉시 대응 필요
```

**프론트엔드 비유**:
```javascript
console.log()    → log.info()
console.warn()   → log.warn()
console.error()  → log.error()
```

#### 구조화된 로깅

```java
// 나쁜 로그
log.info("User " + userId + " created post " + postId);

// 좋은 로그 (구조화)
log.info("User created post", 
    kv("userId", userId),
    kv("postId", postId),
    kv("action", "post.created")
);
```

---

### 2. N+1 문제

#### 문제 상황

```java
// 게시글 10개 조회
List<Post> posts = postRepository.findAll();  // 1번 쿼리

// 각 게시글의 작성자 조회
for (Post post : posts) {
    User author = post.getAuthor();  // N번 쿼리 (10번)
    System.out.println(author.getName());
}

// 총 11번 쿼리! (1 + N)
```

#### 해결 방법

**방법 1: Fetch Join**
```java
@Query("SELECT p FROM Post p JOIN FETCH p.author")
List<Post> findAllWithAuthor();
// 1번 쿼리로 해결
```

**방법 2: EntityGraph**
```java
@EntityGraph(attributePaths = {"author", "board"})
List<Post> findAll();
```

**방법 3: Batch Size**
```java
@Entity
public class Post {
    @ManyToOne(fetch = FetchType.LAZY)
    @BatchSize(size = 10)
    private User author;
}
```

---

### 3. 캐싱 (Caching)

#### 언제 캐싱?

```
자주 조회되는 데이터:
- 게시판 목록 (거의 변하지 않음)
- 인기 게시글
- 사용자 프로필

잘 변하지 않는 데이터:
- 설정 정보
- 코드 데이터
```

#### Redis 캐싱

```
요청: 게시글 1번 조회
    ↓
Redis에 있나? 
    ├─ 있음: Redis에서 반환 (빠름)
    └─ 없음: DB 조회 → Redis에 저장 → 반환
```

**프론트엔드 비유**: React Query, SWR
```javascript
// React Query - 자동 캐싱
const { data } = useQuery('posts', fetchPosts);
// 같은 키로 재요청 시 캐시에서 반환
```

---

## 🛠️ 최소 구현 코드

### 1. 로깅 설정 (Logback)

#### logback-spring.xml
```xml
<!-- src/main/resources/logback-spring.xml -->

<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <!-- Console Appender -->
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <!-- File Appender -->
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/application.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>logs/application-%d{yyyy-MM-dd}.log</fileNamePattern>
            <maxHistory>30</maxHistory>
        </rollingPolicy>
        <encoder>
            <pattern>%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <!-- 레벨 설정 -->
    <root level="INFO">
        <appender-ref ref="CONSOLE" />
        <appender-ref ref="FILE" />
    </root>
    
    <!-- 특정 패키지 레벨 -->
    <logger name="com.project.board" level="DEBUG" />
    <logger name="org.hibernate.SQL" level="DEBUG" />
</configuration>
```

#### Service에서 로깅 사용

```java
@Service
@Slf4j  // Lombok
@RequiredArgsConstructor
public class PostService {
    
    private final PostRepository postRepository;
    
    public Post create(Post post) {
        log.info("게시글 생성 시작: title={}", post.getTitle());
        
        try {
            Post savedPost = postRepository.save(post);
            log.info("게시글 생성 성공: id={}", savedPost.getId());
            return savedPost;
        } catch (Exception e) {
            log.error("게시글 생성 실패", e);
            throw e;
        }
    }
    
    public Post findById(Long id) {
        log.debug("게시글 조회: id={}", id);
        
        return postRepository.findById(id)
                .orElseThrow(() -> {
                    log.warn("게시글 없음: id={}", id);
                    return new ResourceNotFoundException("게시글 없음");
                });
    }
}
```

---

### 2. N+1 문제 해결

#### Fetch Join 적용

```java
// PostRepository.java

public interface PostRepository extends JpaRepository<Post, Long> {
    
    // N+1 문제 해결: author 함께 조회
    @Query("SELECT p FROM Post p " +
           "LEFT JOIN FETCH p.author " +
           "LEFT JOIN FETCH p.board")
    List<Post> findAllWithAuthorAndBoard();
    
    // 페이징과 함께 사용
    @Query(value = "SELECT p FROM Post p LEFT JOIN FETCH p.author",
           countQuery = "SELECT COUNT(p) FROM Post p")
    Page<Post> findAllWithAuthor(Pageable pageable);
}
```

#### EntityGraph 적용

```java
public interface PostRepository extends JpaRepository<Post, Long> {
    
    @EntityGraph(attributePaths = {"author", "board", "replies"})
    Optional<Post> findById(Long id);
    
    @EntityGraph(attributePaths = {"author"})
    Page<Post> findAll(Pageable pageable);
}
```

#### 쿼리 최적화 확인

```properties
# application.properties

# SQL 로그 출력
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# 쿼리 파라미터 출력
logging.level.org.hibernate.type.descriptor.sql.BasicBinder=TRACE

# 쿼리 개수 카운트
logging.level.org.hibernate.stat=DEBUG
spring.jpa.properties.hibernate.generate_statistics=true
```

---

### 3. Redis 캐싱

#### 의존성 추가

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-data-redis'
    implementation 'org.springframework.boot:spring-boot-starter-cache'
}
```

#### application.yml

```yaml
spring:
  redis:
    host: localhost
    port: 6379

  cache:
    type: redis
    redis:
      time-to-live: 600000  # 10분 (ms)
```

#### 캐시 설정

```java
// com/project/board/config/CacheConfig.java

@Configuration
@EnableCaching  // 캐싱 활성화
public class CacheConfig {
    
    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory connectionFactory) {
        RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10))  // TTL 10분
            .serializeValuesWith(
                RedisSerializationContext.SerializationPair.fromSerializer(
                    new GenericJackson2JsonRedisSerializer()
                )
            );
        
        return RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(config)
            .build();
    }
}
```

#### Service에 캐싱 적용

```java
@Service
@RequiredArgsConstructor
@Slf4j
public class PostService {
    
    private final PostRepository postRepository;
    
    // 조회 시 캐싱
    @Cacheable(value = "posts", key = "#id")
    public Post findById(Long id) {
        log.info("DB에서 조회: id={}", id);  // 첫 호출에만 실행
        return postRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("게시글 없음"));
    }
    
    // 생성 시 캐시 무효화
    @CacheEvict(value = "posts", allEntries = true)
    public Post create(Post post) {
        return postRepository.save(post);
    }
    
    // 수정 시 해당 캐시만 무효화
    @CacheEvict(value = "posts", key = "#id")
    public Post update(Long id, Post post) {
        Post existingPost = findById(id);
        existingPost.setTitle(post.getTitle());
        existingPost.setContent(post.getContent());
        return postRepository.save(existingPost);
    }
    
    // 삭제 시 캐시 무효화
    @CacheEvict(value = "posts", key = "#id")
    public void delete(Long id) {
        postRepository.deleteById(id);
    }
}
```

#### Redis 실행 (Docker)

```bash
docker run -d -p 6379:6379 --name redis redis:7
```

---

### 4. 성능 모니터링 (Actuator)

#### 의존성 추가

```gradle
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-actuator'
    implementation 'io.micrometer:micrometer-registry-prometheus'
}
```

#### application.yml

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  
  metrics:
    tags:
      application: ${spring.application.name}
```

#### Endpoint 확인

```
# 헬스 체크
GET http://localhost:8080/actuator/health

# 메트릭
GET http://localhost:8080/actuator/metrics

# JVM 메모리
GET http://localhost:8080/actuator/metrics/jvm.memory.used

# HTTP 요청 수
GET http://localhost:8080/actuator/metrics/http.server.requests
```

---

### 5. 분산 추적 (Spring Cloud Sleuth)

#### 의존성 추가

```gradle
dependencies {
    implementation 'org.springframework.cloud:spring-cloud-starter-sleuth'
    implementation 'org.springframework.cloud:spring-cloud-sleuth-zipkin'
}
```

#### application.yml

```yaml
spring:
  sleuth:
    sampler:
      probability: 1.0  # 100% 샘플링 (개발 환경)
  
  zipkin:
    base-url: http://localhost:9411
```

#### Zipkin 실행

```bash
docker run -d -p 9411:9411 openzipkin/zipkin
```

**Zipkin UI 접속**: http://localhost:9411

---

## 📝 실습 가이드

### Step 1: 로깅 테스트
1. `logback-spring.xml` 생성
2. Service에 로그 추가
3. `logs/application.log` 파일 확인

### Step 2: N+1 문제 확인 및 해결
```
# 1. N+1 문제 확인
spring.jpa.show-sql=true

# 2. 쿼리 개수 확인
GET /api/posts
→ 콘솔에서 쿼리 개수 확인

# 3. Fetch Join 적용
→ 쿼리 1개로 감소 확인
```

### Step 3: 캐싱 테스트
```
# 1. Redis 실행
docker run -d -p 6379:6379 redis

# 2. 첫 호출 (DB 조회)
GET /api/posts/1
→ 로그: "DB에서 조회"

# 3. 두 번째 호출 (캐시)
GET /api/posts/1
→ 로그 없음 (캐시에서 반환)

# 4. Redis 확인
redis-cli
> KEYS *
> GET posts::1
```

### Step 4: Actuator 확인
```
GET http://localhost:8080/actuator/health
GET http://localhost:8080/actuator/metrics
```

---

## 🎓 다음 단계로

### 이 단계에서 배운 것
- ✅ 구조화된 로깅
- ✅ N+1 문제 해결
- ✅ Redis 캐싱
- ✅ Actuator 모니터링
- ✅ 분산 추적 (Zipkin)

### 마지막 단계: Step 10 - 최종 프로젝트 완성

**Step 10에서 할 것**:
1. **프론트엔드 연동**: React로 UI 개발
2. **CI/CD**: GitHub Actions로 자동 배포
3. **전체 시스템 통합**: 모든 기능 통합
4. **프로덕션 배포**: 실제 배포 경험

---

**준비되셨나요? Step 10으로 넘어가서 프로젝트를 완성합시다! 🚀**

```bash
# 다음 문서
dont_upload/Step_10_최종_프로젝트.md
```

