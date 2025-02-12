/*
 * Generic hashmap manipulation functions
 *
 * Originally by Elliot C Back - http://elliottback.com/wp/hashmap-implementation-in-c/
 *
 * Modified by Pete Warden to fix a serious performance problem, support strings as keys
 * and removed thread synchronization - http://petewarden.typepad.com
 */
#ifndef __HASHMAP_H__
#define __HASHMAP_H__

#define MAP_MISSING -3  /* No such element */
#define MAP_FULL 	-2 	/* Hashmap is full */
#define MAP_OMEM 	-1 	/* Out of Memory */
#define MAP_OK		 0 	/* OK */
#define MAP_USED	-4 	/* Collision */
#define MAP_BUSY	-5 	/* Thread Safe */

#include "hash.h"

#define KEY_MAX_LENGTH (256)
#define HASHFUN BKDR_hash
unsigned int (*hash_fun)(char *keystring);

#define MAX_CHAIN_LENGTH (8)

/*
 * data_struct_s is only for hashmap_inc
 */
typedef struct data_struct_s
{
    char* key_string;
    int   number;
} data_struct_t;

/*
 * any_t is a pointer.  This allows you to put arbitrary structures in
 * the hashmap.
 */
typedef void *any_t;

/*
 * PFany is a pointer to a function that can take two any_t arguments
 * and return an integer. Returns status code..
 */
typedef int (*PFany)(any_t, any_t);

/*
 * map_t is a pointer to an internally maintained data structure.
 * Clients of this package do not need to know how hashmaps are
 * represented.  They see and manipulate only map_t's.
 */
typedef any_t map_t;
#if defined(__cplusplus)
extern "C" {
#endif

/*
 * Return an empty hashmap. Returns NULL if empty.
*/
map_t hashmap_new();

/*
 * Iteratively call f with argument (item, data) for
 * each element data in the hashmap. The function must
 * return a map status code. If it returns anything other
 * than MAP_OK the traversal is terminated. f must
 * not reenter any hashmap functions, or deadlock may arise.
 */
int hashmap_iterate(map_t in, PFany f, any_t item);

/*
 * Add/Inc an element number of the hashmap. Return MAP_OK or MAP_OMEM.
 */
int hashmap_inc(map_t in, char* key);

/*
 * Add an element to the hashmap. Return MAP_OK or MAP_OMEM.
 */
int hashmap_put(map_t in, char* key, any_t value);

/*
 * Get an element from the hashmap. Return MAP_OK or MAP_MISSING.
 */
int hashmap_get(map_t in, char* key, any_t *arg);

/*
 * Remove an element from the hashmap. Return MAP_OK or MAP_MISSING.
 */
int hashmap_remove(map_t in, char* key);

/*
 * Get any element. Return MAP_OK or MAP_MISSING.
 * remove - should the element be removed from the hashmap
 */
int hashmap_get_one(map_t in, any_t *arg, int remove);

/*
 * Print a hashmap
 */
void hashmap_print(map_t in, char* log_file);

/*
 * Free the hashmap
 */
void hashmap_free(map_t in);

/*
 * Empty the hashmap
 */
void hashmap_empty(map_t in);

/*
 * Get the current size of a hashmap
 */
int hashmap_length(map_t in);

//////////////////////////////////////////////////////////////////////////////////

void init_log(char* path);
void init_log_number(int number_threshold);
void close_log();

//log_writer("Alloc: %s", key);
void log_writer(int newline, const char *fmt, ...);


#if defined(__cplusplus)
}
#endif

#endif /*__HASHMAP_H__*/
